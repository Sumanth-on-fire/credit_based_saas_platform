import { create } from 'zustand';
import api from '@/lib/api';

export interface Task {
  id: number;
  image_path: string;
  metadata: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  result_path: string | null;
  error_message: string | null;
  credits_used: number;
  created_at: string;
  updated_at: string;
}

interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (formData: FormData) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get('/tasks');
      set({ tasks: response.data, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch tasks', loading: false });
    }
  },

  createTask: async (formData: FormData) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/tasks', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      set((state) => ({
        tasks: [response.data, ...state.tasks],
        loading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to create task', loading: false });
    }
  },
})); 