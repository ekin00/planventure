import Home from '../pages/Home';
import WelcomePage from '../pages/WelcomePage';
import Dashboard from '../pages/Dashboard';
import DashboardLayout from '../layouts/DashboardLayout';
import NewTripPage from '../pages/NewTripPage';
import TripDetailsPage from '../pages/TripDetailsPage';
import EditTripPage from '../pages/EditTripPage';

export const publicRoutes = [
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/welcome',
    element: <WelcomePage />,
  }
];

export const protectedRoutes = [
  {
    path: '/dashboard',
    element: <DashboardLayout><Dashboard /></DashboardLayout>,
  },
  {
    path: '/trips',
    element: <DashboardLayout><Dashboard /></DashboardLayout>,
  },
  {
    path: '/trips/new',
    element: <DashboardLayout><NewTripPage /></DashboardLayout>,
  },
  {
    path: '/trips/:tripId',
    element: <DashboardLayout><TripDetailsPage /></DashboardLayout>,
  },
  {
    path: '/trips/:tripId/edit',
    element: <DashboardLayout><EditTripPage /></DashboardLayout>,
  }
];