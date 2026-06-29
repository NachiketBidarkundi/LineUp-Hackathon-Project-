import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import Landing from "@/pages/Landing";
import SearchPage from "@/pages/Search";
import PlayerProfile from "@/pages/PlayerProfile";
import ComparePage from "@/pages/Compare";
import Shortlist from "@/pages/Shortlist";
import UploadPage from "@/pages/Upload";
import MlbReference from "@/pages/MlbReference";

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/player/:id" element={<PlayerProfile />} />
          <Route path="/mlb" element={<MlbReference />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/shortlist" element={<Shortlist />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
