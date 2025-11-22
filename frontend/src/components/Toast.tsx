import { Toaster } from 'sonner';

export const Toast = () => {
  return (
    <Toaster
      position="top-right"
      theme="dark"
      richColors
      expand={false}
      duration={4000}
      closeButton
      toastOptions={{
        style: {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          color: '#ffffff',
        },
        className: 'custom-toast',
      }}
    />
  );
};

export default Toast;
