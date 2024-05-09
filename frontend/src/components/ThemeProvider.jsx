import { useSelector } from 'react-redux';

export default function ThemeProvider({ children }) {
  const { theme } = useSelector((state) => state.theme);
  return (
    <div className={theme}>
      <div className='bg-gradient-to-br from-slate-50 to-white via-slate-100 text-gray-900 dark:text-white dark:bg-neutral-300 min-h-screen'>
        {children}
      </div>
    </div>
  );
}
