export interface RunCommandRequest {
  command: string;
}

export interface RunCommandResponse {
  success: boolean;
  command: string;
  agent: string;
  status: string;
  result: string;
}