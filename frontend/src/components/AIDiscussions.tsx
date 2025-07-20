import React, { useEffect, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  Forum,
  CheckCircle,
  RadioButtonChecked,
  Schedule,
  SmartToy,
  Psychology,
  Lightbulb,
  QuestionAnswer,
} from '@mui/icons-material';
import { AgentDiscussion, DiscussionMessage } from '../types';

interface AIDiscussionsProps {
  discussions: AgentDiscussion[];
  isGenerating: boolean;
}

const AIDiscussions: React.FC<AIDiscussionsProps> = ({ discussions, isGenerating }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [discussions]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <RadioButtonChecked className="text-green-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="text-green-600" />;
      default:
        return <Schedule className="text-gray-400" />;
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'suggestion':
        return <Lightbulb className="text-yellow-500" fontSize="small" />;
      case 'question':
        return <QuestionAnswer className="text-blue-500" fontSize="small" />;
      case 'decision':
        return <CheckCircle className="text-green-500" fontSize="small" />;
      default:
        return <Forum className="text-gray-500" fontSize="small" />;
    }
  };

  const getAgentAvatar = (agentName: string) => {
    const avatarMap: { [key: string]: string } = {
      'ScriptMaster': '📝',
      'ViralismSpecialist': '🧠',
      'ContentSpecialist': '🎯',
      'VisualDirector': '🎨',
      'AudioEngineer': '🎵',
      'VideoEditor': '✂️',
      'QualityController': '🛡️',
      'TrendAnalyst': '📈',
      'Director': '🎬',
    };
    return avatarMap[agentName] || '🤖';
  };

  if (!isGenerating && discussions.length === 0) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <Forum className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              AI Agent Discussions
            </Typography>
          </Box>
          
          <Box className="text-center py-8">
            <SmartToy className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Ready for AI Collaboration
            </Typography>
            <Typography variant="body2" className="text-gray-500 mb-4">
              AI agents will discuss strategy and optimize your content in real-time
            </Typography>
            
            {/* Preview Discussion Types */}
            <Box className="max-w-md mx-auto space-y-3">
              <Box className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <Typography variant="subtitle2" className="font-semibold text-blue-800">
                  📝 ScriptMaster ↔ 🧠 ViralismSpecialist
                </Typography>
                <Typography variant="caption" className="text-blue-600">
                  Script optimization with viral psychology
                </Typography>
              </Box>
              
              <Box className="p-3 bg-green-50 rounded-lg border border-green-200">
                <Typography variant="subtitle2" className="font-semibold text-green-800">
                  🎯 ContentSpecialist ↔ 🎨 VisualDirector
                </Typography>
                <Typography variant="caption" className="text-green-600">
                  Content strategy meets visual storytelling
                </Typography>
              </Box>
              
              <Box className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                <Typography variant="subtitle2" className="font-semibold text-purple-800">
                  🎵 AudioEngineer ↔ ✂️ VideoEditor
                </Typography>
                <Typography variant="caption" className="text-purple-600">
                  Audio-visual integration and final assembly
                </Typography>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const activeDiscussions = discussions.filter(d => d.status === 'active');
  const completedDiscussions = discussions.filter(d => d.status === 'completed');
  const pendingDiscussions = discussions.filter(d => d.status === 'pending');

  return (
    <Card className="w-full shadow-lg">
      <CardContent className="p-6">
        <Box className="flex items-center justify-between mb-6">
          <Box className="flex items-center">
            <Forum className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              AI Agent Discussions
            </Typography>
          </Box>
          <Box className="flex space-x-2">
            {activeDiscussions.length > 0 && (
              <Chip
                label={`${activeDiscussions.length} Active`}
                color="primary"
                size="small"
                icon={<RadioButtonChecked />}
              />
            )}
            {completedDiscussions.length > 0 && (
              <Chip
                label={`${completedDiscussions.length} Completed`}
                color="success"
                size="small"
                icon={<CheckCircle />}
              />
            )}
          </Box>
        </Box>

        <Box ref={scrollRef} className="max-h-96 overflow-y-auto custom-scrollbar space-y-4">
          {/* Active Discussions */}
          {activeDiscussions.map((discussion) => (
            <DiscussionCard
              key={discussion.id}
              discussion={discussion}
              isActive={true}
            />
          ))}

          {/* Completed Discussions */}
          {completedDiscussions.map((discussion) => (
            <DiscussionCard
              key={discussion.id}
              discussion={discussion}
              isActive={false}
            />
          ))}

          {/* Pending Discussions */}
          {pendingDiscussions.map((discussion) => (
            <Box
              key={discussion.id}
              className="p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
            >
              <Box className="flex items-center justify-between">
                <Box className="flex items-center space-x-3">
                  <Schedule className="text-gray-400" />
                  <Typography variant="subtitle1" className="font-semibold text-gray-600">
                    {discussion.participants.join(' ↔ ')}
                  </Typography>
                </Box>
                <Chip label="Pending" size="small" variant="outlined" />
              </Box>
              <Typography variant="body2" className="text-gray-500 mt-2">
                {discussion.topic}
              </Typography>
            </Box>
          ))}

          {discussions.length === 0 && isGenerating && (
            <Box className="text-center py-8">
              <div className="animate-pulse">
                <Psychology className="text-primary-500 mb-4" style={{ fontSize: 48 }} />
              </div>
              <Typography variant="h6" className="text-gray-700 mb-2">
                Preparing AI Discussions...
              </Typography>
              <Typography variant="body2" className="text-gray-500">
                AI agents are analyzing your request and preparing strategic discussions
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

interface DiscussionCardProps {
  discussion: AgentDiscussion;
  isActive: boolean;
}

const DiscussionCard: React.FC<DiscussionCardProps> = ({ discussion, isActive }) => {
  const getAgentAvatar = (agentName: string) => {
    const avatarMap: { [key: string]: string } = {
      'ScriptMaster': '📝',
      'ViralismSpecialist': '🧠',
      'ContentSpecialist': '🎯',
      'VisualDirector': '🎨',
      'AudioEngineer': '🎵',
      'VideoEditor': '✂️',
      'QualityController': '🛡️',
      'TrendAnalyst': '📈',
      'Director': '🎬',
    };
    return avatarMap[agentName] || '🤖';
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'suggestion':
        return <Lightbulb className="text-yellow-500" fontSize="small" />;
      case 'question':
        return <QuestionAnswer className="text-blue-500" fontSize="small" />;
      case 'decision':
        return <CheckCircle className="text-green-500" fontSize="small" />;
      default:
        return <Forum className="text-gray-500" fontSize="small" />;
    }
  };

  return (
    <Accordion
      className={`border-2 ${isActive 
        ? 'border-green-300 bg-green-50' 
        : 'border-gray-200 bg-white'
      } rounded-lg shadow-sm`}
    >
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box className="flex items-center justify-between w-full mr-4">
          <Box className="flex items-center space-x-3">
            {isActive ? (
              <RadioButtonChecked className="text-green-500 animate-pulse" />
            ) : (
              <CheckCircle className="text-green-600" />
            )}
            <Typography variant="subtitle1" className="font-semibold">
              {discussion.participants.map((participant, index) => (
                <span key={participant}>
                  {getAgentAvatar(participant)} {participant}
                  {index < discussion.participants.length - 1 && ' ↔ '}
                </span>
              ))}
            </Typography>
          </Box>
          <Chip
            label={discussion.status}
            size="small"
            color={isActive ? 'primary' : 'success'}
            variant={isActive ? 'filled' : 'outlined'}
          />
        </Box>
      </AccordionSummary>
      
      <AccordionDetails>
        <Box>
          <Typography variant="body2" className="font-medium text-gray-700 mb-3">
            Topic: {discussion.topic}
          </Typography>
          
          {discussion.messages && discussion.messages.length > 0 && (
            <Box className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
              {discussion.messages.map((message: DiscussionMessage) => (
                <Box
                  key={message.id}
                  className="flex space-x-3 p-3 bg-white rounded-lg border border-gray-100"
                >
                  <Avatar
                    className="w-8 h-8 text-sm"
                    sx={{ bgcolor: '#f3f4f6', color: '#374151' }}
                  >
                    {getAgentAvatar(message.agentName)}
                  </Avatar>
                  <Box className="flex-1">
                    <Box className="flex items-center space-x-2 mb-1">
                      <Typography variant="caption" className="font-semibold text-gray-700">
                        {message.agentName}
                      </Typography>
                      {getMessageIcon(message.type)}
                      <Typography variant="caption" className="text-gray-500">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" className="text-gray-600">
                      {message.content}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          )}
          
          {discussion.summary && (
            <Box className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <Typography variant="caption" className="font-semibold text-blue-800 block mb-1">
                Discussion Summary:
              </Typography>
              <Typography variant="body2" className="text-blue-700">
                {discussion.summary}
              </Typography>
            </Box>
          )}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default AIDiscussions;