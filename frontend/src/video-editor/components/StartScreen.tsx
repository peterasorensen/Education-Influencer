import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ToolbarContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  animation: fadeIn 0.3s ease-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.5px;
  filter: drop-shadow(0 2px 8px rgba(124, 58, 237, 0.4));
`;

const ButtonContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const OptionButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: none;
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  white-space: nowrap;
  position: relative;

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const Divider = styled.div`
  width: 1px;
  height: 28px;
  background: ${({ theme }) => theme.colors.border.primary};
`;

interface StartScreenProps {
  onScreenRecord?: () => void;
  onEdit?: () => void;
}

const StartScreen: React.FC<StartScreenProps> = ({ onScreenRecord, onEdit }) => {
  return (
    <Container>
      <ToolbarContainer>
        <Title>Clip Forge</Title>

        <ButtonContainer>
          <OptionButton onClick={onScreenRecord}>
            Screen Record
          </OptionButton>

          <Divider />

          <OptionButton onClick={onEdit}>
            Edit
          </OptionButton>
        </ButtonContainer>
      </ToolbarContainer>
    </Container>
  );
};

export default StartScreen;
