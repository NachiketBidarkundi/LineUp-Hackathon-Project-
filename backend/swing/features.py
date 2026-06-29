"""Compute 5 biomech features from a (frames, 33, 3) pose array."""
import numpy as np

# MediaPipe Pose landmark indices
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_HIP, R_HIP = 23, 24
L_WRIST, R_WRIST = 15, 16

FPS = 30  # videos are 29.97fps (verified with cv2)


def _angle_xz_deg(p1, p2):
    """Angle (degrees) of vector p1->p2 in the XZ horizontal plane (top-down)."""
    dx = p2[..., 0] - p1[..., 0]
    dz = p2[..., 2] - p1[..., 2]
    return np.degrees(np.arctan2(dz, dx))


def _interp_nans(arr):
    """Linear interp NaNs along a 1D array."""
    arr = arr.copy()
    nans = np.isnan(arr)
    if nans.all() or not nans.any():
        return arr
    x = np.arange(len(arr))
    arr[nans] = np.interp(x[nans], x[~nans], arr[~nans])
    return arr


def _dominant_wrist_speed(pose):
    """Per-frame speed (m/frame) of whichever wrist moves most. NaNs interpolated."""
    lw_range = np.nanmax(pose[:, L_WRIST, 0]) - np.nanmin(pose[:, L_WRIST, 0])
    rw_range = np.nanmax(pose[:, R_WRIST, 0]) - np.nanmin(pose[:, R_WRIST, 0])
    idx = L_WRIST if lw_range > rw_range else R_WRIST
    wx, wy, wz = (_interp_nans(pose[:, idx, k]) for k in range(3))
    speed = np.sqrt(np.gradient(wx) ** 2 + np.gradient(wy) ** 2 + np.gradient(wz) ** 2)
    return speed, idx


def crop_to_swing(pose: np.ndarray, pad_s: float = 0.4,
                  thresh_frac: float = 0.25, max_s: float = 6.0) -> np.ndarray:
    """Isolate a single swing from a clip that may contain lead-up / multiple swings.

    Contact = frame of peak wrist speed. We expand outward from there while the
    (smoothed) wrist speed stays above thresh_frac * peak, then pad a little. This
    keeps one swing's motion envelope regardless of slow-mo factor, so features
    like hip_shoulder_separation (which unwraps angle) don't accumulate across
    multiple swings. Returns the cropped pose array.
    """
    n = len(pose)
    if n < 8:
        return pose
    speed, _ = _dominant_wrist_speed(pose)
    # smooth to avoid latching onto a single-frame spike
    k = max(1, int(round(0.1 * FPS)))
    kernel = np.ones(2 * k + 1) / (2 * k + 1)
    sm = np.convolve(speed, kernel, mode="same")

    contact = int(np.argmax(sm))
    thresh = thresh_frac * sm[contact]
    lo = contact
    while lo > 0 and sm[lo - 1] > thresh:
        lo -= 1
    hi = contact
    while hi < n - 1 and sm[hi + 1] > thresh:
        hi += 1

    pad = int(round(pad_s * FPS))
    lo = max(0, lo - pad)
    hi = min(n, hi + pad + 1)
    # clamp to a sane max window centred on contact
    max_f = int(round(max_s * FPS))
    if hi - lo > max_f:
        lo = max(0, contact - max_f // 2)
        hi = min(n, lo + max_f)
    return pose[lo:hi]


def compute_features(pose: np.ndarray, auto_crop: bool = True) -> dict:
    """Input: pose array (frames, 33, 3) world landmarks in meters. Output: 5 features.

    By default auto-crops to a single swing so untrimmed clips work.
    """
    if auto_crop:
        pose = crop_to_swing(pose)

    # --- Hip & shoulder rotation in horizontal plane (top-down) ---
    hip_raw = _angle_xz_deg(pose[:, L_HIP], pose[:, R_HIP])
    sho_raw = _angle_xz_deg(pose[:, L_SHOULDER], pose[:, R_SHOULDER])
    hip = np.degrees(np.unwrap(np.deg2rad(_interp_nans(hip_raw))))
    sho = np.degrees(np.unwrap(np.deg2rad(_interp_nans(sho_raw))))

    separation = np.abs(sho - hip)
    hip_shoulder_separation = float(np.nanmax(separation))  # peak across swing

    # --- Head stability: max range of nose XY position, in cm ---
    nose_x = _interp_nans(pose[:, NOSE, 0])
    nose_y = _interp_nans(pose[:, NOSE, 1])
    head_range_m = np.sqrt(
        (nose_x.max() - nose_x.min()) ** 2 + (nose_y.max() - nose_y.min()) ** 2
    )
    head_stability = float(head_range_m * 100)

    # --- Pick dominant wrist (greater range of motion) ---
    lw_range = np.nanmax(pose[:, L_WRIST, 0]) - np.nanmin(pose[:, L_WRIST, 0])
    rw_range = np.nanmax(pose[:, R_WRIST, 0]) - np.nanmin(pose[:, R_WRIST, 0])
    wrist_idx = L_WRIST if lw_range > rw_range else R_WRIST
    wx = _interp_nans(pose[:, wrist_idx, 0])
    wy = _interp_nans(pose[:, wrist_idx, 1])
    wz = _interp_nans(pose[:, wrist_idx, 2])
    wrist_speed = np.sqrt(np.gradient(wx) ** 2 + np.gradient(wy) ** 2 + np.gradient(wz) ** 2)

    # --- Kinematic sequence: hips peak vel → torso peak vel → hands peak vel ---
    hip_vel = np.abs(np.gradient(hip))
    sho_vel = np.abs(np.gradient(sho))
    t_hip = int(np.argmax(hip_vel))
    t_sho = int(np.argmax(sho_vel))
    t_hand = int(np.argmax(wrist_speed))
    kinematic_sequence = 1 if (t_hip <= t_sho <= t_hand) else 0

    # --- Bat speed proxy: peak wrist speed converted to mph ---
    # m/frame * FPS = m/s ; * 2.237 = mph
    bat_speed_proxy = float(wrist_speed.max() * FPS * 2.237)

    # --- Swing tempo: frames from load (min wrist y, hands lowest) to contact (peak wrist speed) ---
    load_frame = int(np.argmin(wy))
    swing_tempo = int(max(0, t_hand - load_frame))

    return {
        "hip_shoulder_separation": hip_shoulder_separation,
        "head_stability": head_stability,
        "kinematic_sequence": kinematic_sequence,
        "bat_speed_proxy": bat_speed_proxy,
        "swing_tempo": swing_tempo,
    }


if __name__ == "__main__":
    import sys, json
    from pose_extract import extract_pose
    feats = compute_features(extract_pose(sys.argv[1]))
    print(json.dumps(feats, indent=2))