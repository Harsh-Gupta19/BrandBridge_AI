import { createBrowserRouter } from "react-router-dom";

import { AppLayout } from "../components/AppLayout";
import { BrandPage } from "../pages/BrandPage";
import { CampaignDetailPage } from "../pages/CampaignDetailPage";
import { CampaignsPage } from "../pages/CampaignsPage";
import { CreatorPage } from "../pages/CreatorPage";
import { CreatorProfilePage } from "../pages/CreatorProfilePage";
import { CreatorsPage } from "../pages/CreatorsPage";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";
import { ProposalsPage } from "../pages/ProposalsPage";
import { RecommendationsPage } from "../pages/RecommendationsPage";
import { RegisterPage } from "../pages/RegisterPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      { path: "creator", element: <CreatorPage /> },
      { path: "brand", element: <BrandPage /> },
      { path: "campaigns", element: <CampaignsPage /> },
      { path: "campaigns/:id", element: <CampaignDetailPage /> },
      { path: "creators", element: <CreatorsPage /> },
      { path: "creators/:id", element: <CreatorProfilePage /> },
      { path: "recommendations", element: <RecommendationsPage /> },
      { path: "proposals", element: <ProposalsPage /> },
    ],
  },
]);
