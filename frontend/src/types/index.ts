export interface VideoGenerationConfig {
  mission: string;
  category: 'Comedy' | 'Educational' | 'Entertainment' | 'News' | 'Tech' | 'Health' | 'Lifestyle';
  platform: 'youtube' | 'tiktok' | 'instagram' | 'twitter';
  duration: number;
  imageOnly: boolean;
  fallbackOnly: boolean;
  force: boolean;
  skipAuthTest: boolean;
  discussions: 'off' | 'light' | 'standard' | 'deep' | 'streamlined' | 'enhanced';
  discussionLog: boolean;
  sessionId?: string;
  frameContinuity: 'auto' | 'on' | 'off';
  targetAudience?: string;
  style?: string;
  tone?: string;
  visualStyle?: string;
  mode: 'simple' | 'enhanced' | 'advanced' | 'professional';
}

export interface AgentStatus {
  id: string;
  name: string;
  emoji: string;
  description: string;
  status: 'idle' | 'active' | 'completed' | 'error';
  progress: number;
  currentTask?: string;
  lastUpdate: Date;
}

export interface AgentDiscussion {
  id: string;
  sessionId: string;
  participants: string[];
  topic: string;
  messages: DiscussionMessage[];
  status: 'pending' | 'active' | 'completed';
  timestamp: Date;
  summary?: string;
}

export interface DiscussionMessage {
  id: string;
  agentId: string;
  agentName: string;
  content: string;
  timestamp: Date;
  type: 'suggestion' | 'question' | 'response' | 'decision';
}

export interface GenerationProgress {
  sessionId: string;
  progress: number;
  currentPhase: string;
  totalPhases: number;
  status: 'initializing' | 'generating' | 'processing' | 'completed' | 'error';
  message: string;
  startTime: Date;
  estimatedCompletion?: Date;
  agents: AgentStatus[];
  discussions: AgentDiscussion[];
}

export interface VideoClip {
  id: string;
  name: string;
  path: string;
  duration: number;
  thumbnail?: string;
  type: 'veo' | 'gemini' | 'fallback';
  status: 'generating' | 'completed' | 'error';
  timestamp: Date;
}

export interface AudioSegment {
  id: string;
  name: string;
  path: string;
  duration: number;
  transcript?: string;
  type: 'voice' | 'music' | 'effects';
  status: 'generating' | 'completed' | 'error';
  timestamp: Date;
}

export interface Script {
  id: string;
  content: string;
  segments: ScriptSegment[];
  metadata: {
    totalDuration: number;
    wordCount: number;
    readingTime: number;
  };
  version: number;
  lastModified: Date;
}

export interface ScriptSegment {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  speaker?: string;
  action?: string;
  isEditable: boolean;
}

export interface Overlay {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  position: {
    x: number;
    y: number;
  };
  style: {
    fontSize: number;
    color: string;
    backgroundColor?: string;
    fontFamily: string;
    fontWeight: 'normal' | 'bold';
  };
  animation?: 'fade' | 'slide' | 'zoom' | 'none';
  isEditable: boolean;
}

export interface Subtitle {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  position: 'bottom' | 'top' | 'center';
  style: {
    fontSize: number;
    color: string;
    backgroundColor?: string;
    fontFamily: string;
  };
  isEditable: boolean;
}

export interface FinalVideo {
  id: string;
  path: string;
  thumbnail: string;
  duration: number;
  size: number;
  format: string;
  resolution: string;
  status: 'processing' | 'completed' | 'error';
  metadata: {
    sessionId: string;
    generatedAt: Date;
    config: VideoGenerationConfig;
    clips: VideoClip[];
    audio: AudioSegment[];
    overlays: Overlay[];
    subtitles: Subtitle[];
  };
}

export interface GenerationSession {
  id: string;
  config: VideoGenerationConfig;
  progress: GenerationProgress;
  script?: Script;
  videoClips: VideoClip[];
  audioSegments: AudioSegment[];
  overlays: Overlay[];
  subtitles: Subtitle[];
  finalVideo?: FinalVideo;
  createdAt: Date;
  updatedAt: Date;
  status: 'active' | 'completed' | 'error' | 'cancelled';
}

export interface WebSocketMessage {
  type: 'progress_update' | 'agent_update' | 'discussion_update' | 'clip_update' | 'audio_update' | 'script_update' | 'completion';
  sessionId: string;
  data: any;
  timestamp: Date;
}