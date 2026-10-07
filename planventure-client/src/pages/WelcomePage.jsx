import AuthLayout from '../layouts/AuthLayout';
import WelcomeForm from '../components/auth/WelcomeForm';

const WelcomePage = () => {
  return (
    <AuthLayout>
      <WelcomeForm />
    </AuthLayout>
  );
};

export default WelcomePage;
