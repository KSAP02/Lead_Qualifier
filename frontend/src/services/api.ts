import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface Lead {
  id?: string;
  name: string;
  company: string;
  industry: string;
  size: number;
  source: string;
  created_at: string;
  quality: string;
  summary: string;
}

export interface EventData {
  action: string;
  data: any;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getLeads = async (industry?: string, size?: number): Promise<Lead[]> => {
  try {
    const params: any = {};
    if (industry) params.industry = industry;
    if (size) params.size = size;

    const response = await api.get('/leads', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching leads:', error);
    throw error;
  }
};

export const postEvent = async (eventData: EventData): Promise<void> => {
  try {
    await api.post('/events', {
      ...eventData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error posting event:', error);
    throw error;
  }
};