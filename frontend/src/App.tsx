import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import MessageScanner from "./pages/MessageScanner";
import UrlScanner from "./pages/UrlScanner";
import Result from "./pages/Result";
import HistoryPage from "./pages/History";
import Intelligence from "./pages/Intelligence";
import Guide from "./pages/Guide";
import About from "./pages/About";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/scan/message" element={<MessageScanner />} />
        <Route path="/scan/url" element={<UrlScanner />} />
        <Route path="/result/:scanId" element={<Result />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/intelligence" element={<Intelligence />} />
        <Route path="/guide" element={<Guide />} />
        <Route path="/about" element={<About />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
