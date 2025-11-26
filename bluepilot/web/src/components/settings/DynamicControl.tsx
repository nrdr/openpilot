/**
 * Dynamic Control Component
 * Routes to the appropriate control component based on control type
 */

import type { PanelControl, PanelState } from '@/types/panels'
import { useParamsStore } from '@/stores/useParamsStore'
import { useFavoritesStore } from '@/stores/useFavoritesStore'
import { isControlVisible, isControlEnabled, getDisabledReason } from '@/utils/conditionalEvaluator'
import {
  ToggleControl,
  SelectionControl,
  SegmentedControl,
  NumberControl,
  CommandButton,
  FileViewer,
  StaticTextControl,
  StaticParamDisplayControl,
  PlatformDisplayControl,
  RecentChangesControl,
  RestartUIControl,
} from './controls'
import './DynamicControl.css'

interface DynamicControlProps {
  control: PanelControl
  state: PanelState
  panelId?: string
  groupName?: string
}

export function DynamicControl({ control, state, panelId, groupName }: DynamicControlProps) {
  const params = useParamsStore((store) => store.params)
  const { isFavorite, addFavorite, removeFavorite } = useFavoritesStore()

  // Check if control is hidden in web UI
  if ('webSupported' in control && control.webSupported === false) {
    return null
  }

  // Check visibility
  if (!isControlVisible(control, state, params)) {
    return null
  }

  // Check if enabled
  const enabled = isControlEnabled(control, state, params)
  const disabledReason = !enabled ? getDisabledReason(control.enableConditions, state, params) : null

  // Check if this control is favorited
  const favorited = panelId && groupName ? isFavorite(panelId, groupName, control.title) : false

  const handleToggleFavorite = () => {
    if (!panelId || !groupName) return

    if (favorited) {
      removeFavorite(panelId, groupName, control.title)
    } else {
      addFavorite({
        panelId,
        groupName,
        controlTitle: control.title,
        param: 'param' in control ? control.param : undefined,
      })
    }
  }

  // Route to appropriate control component
  let controlElement: JSX.Element | null = null

  switch (control.type) {
    case 'toggle':
      controlElement = <ToggleControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'selection':
      controlElement = <SelectionControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'segmented_control':
      controlElement = <SegmentedControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'integer':
    case 'float':
      controlElement = <NumberControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'command_button':
      controlElement = <CommandButton control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'file_viewer':
      controlElement = <FileViewer control={control} disabled={!enabled} />
      break

    case 'recent_changes':
      controlElement = <RecentChangesControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    case 'static_text':
      controlElement = <StaticTextControl control={control} />
      break

    case 'static_param_display':
      controlElement = <StaticParamDisplayControl control={control} />
      break

    case 'platform_display':
      controlElement = <PlatformDisplayControl control={control} />
      break

    case 'restart_ui':
      controlElement = <RestartUIControl control={control} disabled={!enabled} disabledReason={disabledReason} />
      break

    // Unsupported control types (mostly Qt-specific)
    case 'file_param_display':
    case 'param_viewer':
    case 'param_list_viewer':
      controlElement = (
        <div style={{
          padding: '1rem',
          background: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          color: 'var(--text-secondary)',
          fontSize: '0.875rem',
        }}>
          <strong>{control.title}</strong>
          <p style={{ margin: '0.5rem 0 0 0' }}>
            This control type ({control.type}) is not yet supported in the web UI.
            {control.desc && <><br />{control.desc}</>}
          </p>
        </div>
      )
      break

    default:
      console.warn('Unknown control type:', control)
      controlElement = null
  }

  if (!controlElement) return null

  // Wrap control with favorite button (if we have panel context)
  if (panelId && groupName) {
    return (
      <div className="dynamic-control-wrapper">
        <div className="dynamic-control-content">{controlElement}</div>
        <button
          className={`dynamic-control-favorite ${favorited ? 'favorited' : ''}`}
          onClick={handleToggleFavorite}
          title={favorited ? 'Remove from favorites' : 'Add to favorites'}
          aria-label={favorited ? 'Remove from favorites' : 'Add to favorites'}
        >
          {favorited ? '★' : '☆'}
        </button>
      </div>
    )
  }

  return controlElement
}
