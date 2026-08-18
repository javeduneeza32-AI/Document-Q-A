import { createContext, useState, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [role, setRole] = useState(localStorage.getItem('role'));

    const login = async (username, password) => {
        // UPDATED: Uses VITE_API_URL dynamically
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, { username, password });
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('role', res.data.role);
        setToken(res.data.access_token);
        setRole(res.data.role);
        setUser({ username });
        return res;
    };

    const signup = async (username, email, password) => {
        // UPDATED: Uses VITE_API_URL dynamically
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/signup`, { username, email, password });
        return res;
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        setToken(null);
        setRole(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, role, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);