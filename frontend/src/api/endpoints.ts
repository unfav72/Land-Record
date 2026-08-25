import { apiClient } from './client';
import * as Types from '../types';

export const auth = {
  login: async (data: FormData) => {
    const response = await apiClient.post<{ access_token: string }>('/api/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await apiClient.get<Types.User>('/api/auth/me');
    return response.data;
  }
};

export const dashboard = {
  getStats: async () => {
    const response = await apiClient.get<Types.DashboardStats>('/api/dashboard/stats');
    return response.data;
  }
};

export const documents = {
  upload: async (file: File, documentType?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (documentType) {
      formData.append('document_type', documentType);
    }
    const response = await apiClient.post<Types.Document>('/api/documents/upload', formData, {
      headers: {
        'Content-Type': undefined
      }
    });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await apiClient.get<Types.Document>(`/api/documents/${id}`);
    return response.data;
  },
  getJobs: async (id: number) => {
    const response = await apiClient.get<any[]>(`/api/documents/${id}/jobs`);
    return response.data;
  }
};

export const records = {
  list: async (params?: { skip?: number; limit?: number; status?: string }) => {
    const response = await apiClient.get<Types.LandRecord[]>('/api/records/', { params });
    return response.data;
  },
  getById: async (id: number) => {
    const response = await apiClient.get<Types.LandRecord>(`/api/records/${id}`);
    return response.data;
  },
  getValidation: async (id: number) => {
    const response = await apiClient.get<Types.ValidationResult[]>(`/api/records/${id}/validation`);
    return response.data;
  },
  getCorrections: async (id: number) => {
    const response = await apiClient.get<any[]>(`/api/records/${id}/corrections`);
    return response.data;
  },
  correctField: async (id: number, data: { field_name: string; officer_value: string; reason?: string }) => {
    const response = await apiClient.post(`/api/records/${id}/correct`, data);
    return response.data;
  },
  action: async (id: number, action: 'approve' | 'reject' | 'save_draft', rejectionReason?: string) => {
    const response = await apiClient.post<Types.LandRecord>(`/api/records/${id}/action`, {
      action,
      rejection_reason: rejectionReason
    });
    return response.data;
  },
  delete: async (id: number) => {
    const response = await apiClient.delete(`/api/records/${id}`);
    return response.data;
  }
};

export const search = {
  query: async (data: any) => {
    const response = await apiClient.post<Types.LandRecord[]>('/api/search/', data);
    return response.data;
  }
};

export const exports = {
  downloadExcel: async () => {
    const response = await apiClient.get('/api/export/excel', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `land_records_export.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  downloadPDF: async (recordId: number) => {
    const response = await apiClient.get(`/api/export/pdf/${recordId}`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `land_record_${recordId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};
