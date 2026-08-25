export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'officer';
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  status: 'UPLOADING' | 'PREPROCESSING' | 'OCR' | 'CLASSIFICATION' | 'EXTRACTING' | 'VALIDATING' | 'COMPLETED' | 'FAILED';
  document_type?: string;
  document_type_confidence?: number;
  language?: string;
  ocr_confidence?: number;
  handwriting_confidence?: number;
  upload_time: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  error_message?: string;
  file_size?: number;
}

export interface LandRecord {
  id: number;
  document_id: number;
  owner_name?: string;
  father_spouse_name?: string;
  ownership_type?: string;
  survey_number?: string;
  sub_survey_number?: string;
  khasra_number?: string;
  khata_number?: string;
  plot_number?: string;
  village?: string;
  taluk_tehsil?: string;
  district?: string;
  state?: string;
  area?: string;
  area_unit?: string;
  land_classification?: string;
  land_type?: string;
  registration_number?: string;
  registration_date?: string;
  mutation_number?: string;
  mutation_date?: string;
  previous_owner?: string;
  current_owner?: string;
  overall_confidence?: number;
  field_confidences?: string;
  field_sources?: string;
  status: 'DRAFT' | 'NEEDS_REVIEW' | 'VERIFIED' | 'REJECTED' | 'CONFLICT';
  verified_by?: number;
  verified_at?: string;
  rejection_reason?: string;
  pdf_path?: string;
  qr_code_path?: string;
  created_at: string;
  updated_at: string;
}

export interface ValidationResult {
  id: number;
  record_id: number;
  rule_name: string;
  field_name?: string;
  severity: 'INFO' | 'WARNING' | 'ERROR';
  message: string;
  ai_value?: string;
  expected_format?: string;
  is_resolved: boolean;
}

export interface DashboardStats {
  total_documents: number;
  processed: number;
  verified: number;
  needs_review: number;
  conflicts: number;
  rejected: number;
  drafts: number;
  avg_confidence: number;
  languages: Record<string, number>;
  document_types: Record<string, number>;
}
