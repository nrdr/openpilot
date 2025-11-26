/**
 * Toggle Control Component
 * Renders a boolean toggle switch for panel settings
 */

import { useState } from 'react'
import type { ToggleControl as ToggleControlType } from '@/types/panels'
import { useParamsStore } from '@/stores/useParamsStore'
import { usePanelStateStore } from '@/stores/usePanelStateStore'
import { getDynamicDescription, getDynamicTitle, getDynamicStyle } from '@/utils/conditionalEvaluator'
import { ControlCard, ConfirmDialog, ToggleSwitch } from '@/components/common'
import './ToggleControl.css'

interface ToggleControlProps {
  control: ToggleControlType
  disabled?: boolean
  disabledReason?: string | null
}

export function ToggleControl({ control, disabled, disabledReason }: ToggleControlProps) {
  const { params, updateParam } = useParamsStore()
  const panelState = usePanelStateStore((state) => state.state)
  const [showConfirm, setShowConfirm] = useState(false)
  const [pendingValue, setPendingValue] = useState<boolean | null>(null)

  // Get current value
  const currentValue = params[control.param]?.value
  const isEnabled = currentValue === true || currentValue === '1' || currentValue === 1

  // Get dynamic content
  const title = getDynamicTitle(control, panelState, params)
  const description = getDynamicDescription(control, panelState, params)
  const style = getDynamicStyle(control, panelState, params)

  const handleToggle = async () => {
    const newValue = !isEnabled

    // Show confirmation if required
    if (control.confirm || control.confirmation) {
      setPendingValue(newValue)
      setShowConfirm(true)
      return
    }

    // Otherwise, update immediately
    await updateParam(control.param, newValue ? '1' : '0')
  }

  const handleConfirm = async () => {
    if (pendingValue !== null) {
      await updateParam(control.param, pendingValue ? '1' : '0')
      setPendingValue(null)
    }
    setShowConfirm(false)
  }

  const handleCancel = () => {
    setPendingValue(null)
    setShowConfirm(false)
  }

  return (
    <>
      <ControlCard
        title={title}
        description={description}
        disabled={disabled}
        disabledReason={disabledReason}
        layout="inline"
        className="toggle-control-card"
        style={style}
        aside={
          <ToggleSwitch
            checked={isEnabled}
            onChange={() => handleToggle()}
            disabled={disabled}
            aria-label={title}
          />
        }
      />

      <ConfirmDialog
        isOpen={showConfirm}
        onClose={handleCancel}
        onConfirm={handleConfirm}
        title={`${pendingValue ? 'Enable' : 'Disable'} ${title}`}
        message={
          control.confirm_text ? (
            <div dangerouslySetInnerHTML={{ __html: control.confirm_text }} />
          ) : (
            `Are you sure you want to ${pendingValue ? 'enable' : 'disable'} ${title}?`
          )
        }
        confirmText={control.confirm_yes_text || (pendingValue ? 'Enable' : 'Disable')}
        cancelText={control.confirm_no_text || 'Cancel'}
        variant={style?.backgroundColor?.toLowerCase().includes('e22c2c') ? 'danger' : 'warning'}
      />
    </>
  )
}
