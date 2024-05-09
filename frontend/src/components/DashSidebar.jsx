import { Sidebar } from 'flowbite-react';
import {
  HiUser,
  HiArrowSmRight,
  HiDocumentText,
  HiOutlineUserGroup,
  HiAnnotation,
  HiChartPie,
} from 'react-icons/hi';
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { signoutSuccess } from '../redux/user/userSlice';
import { useDispatch } from 'react-redux';
import { useSelector } from 'react-redux';

export default function DashSidebar() {
  const location = useLocation();
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state) => state.user);
  const [tab, setTab] = useState('');
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const tabFromUrl = urlParams.get('tab');
    if (tabFromUrl) {
      setTab(tabFromUrl);
    }
  }, [location.search]);
  const handleSignout = async () => {
    try {
      const res = await fetch('/api/user/signout', {
        method: 'POST',
      });
      const data = await res.json();
      if (!res.ok) {
        console.log(data.message);
      } else {
        dispatch(signoutSuccess());
      }
    } catch (error) {
      console.log(error.message);
    }
  };
  return (
    <Sidebar className='w-full -translate-y-4  md:w-56 dark:bg-cyan-800 bg-gradient-to-br from-slate-50 to-white via-slate-100  '>
      <Sidebar.Items>
        <Sidebar.ItemGroup className='flex flex-col gap-1 '>
          { (
            <Link to='/dashboard?tab=dash'>
              <Sidebar.Item className='hover:bg-slate-400'
                active={tab === 'dash' || !tab}
                icon={HiChartPie}
                as='div'
              >
                Dashboard
              </Sidebar.Item>
            </Link>
          )}
          <Link to='/dashboard?tab=profile'>
            <Sidebar.Item className='hover:bg-slate-400'
              active={tab === 'profile'}
              icon={HiUser}
              label={'User'}
              labelColor='dark'
              as='div'
            >
              Profile
            </Sidebar.Item>
          </Link>
          { (
            <Link to='/dashboard?tab=posts'>
              <Sidebar.Item className='hover:bg-slate-400'
                active={tab === 'posts'}
                icon={HiDocumentText}
                as='div'
              >
                Posts
              </Sidebar.Item>
            </Link>
          )}
          { (
            <>
              <Link to='/dashboard?tab=users'>
                <Sidebar.Item className='hover:bg-slate-400'
                  active={tab === 'users'}
                  icon={HiOutlineUserGroup}
                  as='div'
                >
                  Users
                </Sidebar.Item>
              </Link>
              <Link to='/dashboard?tab=comments'>
                <Sidebar.Item className='hover:bg-slate-400'
                  active={tab === 'comments'}
                  icon={HiAnnotation}
                  as='div'
                >
                  Comments
                </Sidebar.Item>
              </Link>
              <Link to='/dashboard?tab=add_doctor'>
                <Sidebar.Item className='hover:bg-slate-400'
                  active={tab === 'add_doctor'}
                  icon={HiAnnotation}
                  as='div'
                >
                  Add Doctor
                </Sidebar.Item>
              </Link>
              <Link to='/dashboard?tab=comments'>
                <Sidebar.Item className='hover:bg-slate-400'
                  active={tab === 'comments'}
                  icon={HiAnnotation}
                  as='div'
                >
                Look Up History
                </Sidebar.Item>
              </Link>
            </>
          )}
          <Sidebar.Item 
            icon={HiArrowSmRight}
            className='cursor-pointer hover:bg-slate-400'
            onClick={handleSignout}
          >
            Sign Out
          </Sidebar.Item>
        </Sidebar.ItemGroup>
      </Sidebar.Items>
    </Sidebar>
  );
}
