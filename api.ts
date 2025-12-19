import axios from 'axios';

const API_URL = '/api/v1/analysis';

export interface Report {
    id: number;
    image_path: string;
    mask_path?: string;
    total_area?: number;
    usable_area?: number;
    panel_count?: number;
    solar_capacity?: number;
    panel_layout_path?: string;
    created_at: string;
}

export const uploadImage = async (file: File): Promise<Report> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const segmentImage = async (reportId: number): Promise<Report> => {
    const response = await axios.post(`${API_URL}/segment`, { report_id: reportId, model_type: 'pytorch' });
    return response.data;
};

export const calculateArea = async (reportId: number): Promise<Report> => {
    const response = await axios.post(`${API_URL}/calculate`, { report_id: reportId, scale_factor: 0.1 });
    return response.data;
};

export const estimatePanels = async (reportId: number): Promise<Report> => {
    const response = await axios.post(`${API_URL}/panel-estimation`, { report_id: reportId, panel_area: 1.6, panel_wattage: 400 });
    return response.data;
};

export const getReport = async (id: number): Promise<Report> => {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
};
