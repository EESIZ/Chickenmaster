import React from 'react';
import { Tooltip } from 'react-tooltip';

interface Action {
  id: string;
  icon: string;
  label: string;
  duration: string;
  tooltipContent: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

interface ActionBarProps {
  actions: Action[];
}

export const ActionBar: React.FC<ActionBarProps> = ({ actions }) => {
  return (
    <div className="flex justify-center gap-4 p-4 bg-game-secondary border-t border-game-accent">
      {actions.map((action) => (
        <React.Fragment key={action.id}>
          <button
            className={`
              px-6 py-3 rounded
              bg-game-primary text-game-text
              border border-game-accent
              hover:bg-game-accent hover:text-game-primary
              transition-all duration-200
              ${action.disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            onClick={action.onClick}
            disabled={action.disabled}
            data-tooltip-id={`action-${action.id}`}
          >
            {action.icon} {action.label} {action.duration}
          </button>
          <Tooltip
            id={`action-${action.id}`}
            place="top"
            className="z-50 max-w-xs bg-game-primary border border-game-accent text-game-text p-4 rounded"
          >
            {action.tooltipContent}
          </Tooltip>
        </React.Fragment>
      ))}
    </div>
  );
}; 