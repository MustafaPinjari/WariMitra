import axios from 'axios';
import { API_BASE } from '../services/api';
export const api = axios.create({ baseURL: API_BASE });
