import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function AdminDashboard() {
    const [users, setUsers] = useState([]);
    const { token, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                // UPDATED: Uses VITE_API_URL dynamically
                const res = await axios.get(`${import.meta.env.VITE_API_URL}/admin/users`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsers(res.data);
            } catch (err) {
                alert('Admin access denied.');
                navigate('/');
            }
        };
        fetchUsers();
    }, [token, navigate]);

    return (
        <div>
            <h1>Admin Control Panel</h1>
            <button onClick={() => { logout(); navigate('/login'); }}>Logout</button>
            <h3>All Registered Users:</h3>
            <ul>
                {users.map(u => (
                    <li key={u.id}>{u.username} - {u.email} (Role: {u.role})</li>
                ))}
            </ul>
        </div>
    );
}