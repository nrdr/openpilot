/**
 * Segmented Control Component
 * Renders a button group for choosing from multiple options
 */

import type { SegmentedControl as SegmentedControlType } from '@/types/panels'
import { useParamsStore } from '@/stores/useParamsStore'
import { usePanelStateStore } from '@/stores/usePanelStateStore'
import { getDynamicDescription, evaluateConditions } from '@/utils/conditionalEvaluator'
import { ControlCard } from '@/components/common'
import './SegmentedControl.css'

interface SegmentedControlProps {
  control: SegmentedControlType
  disabled?: boolean
  disabledReason?: string | null
}

export function SegmentedControl({ control, disabled, disabledReason }: SegmentedControlProps) {
  const { params, updateParam } = useParamsStore()
  const panelState = usePanelStateStore((state) => state.state)

  // Get current value and normalize to string for comparison
  const rawValue = params[control.param]?.value
  const currentValue = rawValue !== null && rawValue !== undefined ? String(rawValue) : ''

  // Get dynamic description
  const description = getDynamicDescription(control, panelState, params)

  // Filter options based on enableConditions
  const availableOptions = control.options.filter((option) => {
    if (!option.enableConditions) return true
    return evaluateConditions(option.enableConditions, panelState, params)
  })

  const handleSelect = async (value: string) => {
    if (!disabled) {
      await updateParam(control.param, value)
    }
  }

  // Get selected option description (normalize option.value to string for comparison)
  const selectedOption = availableOptions.find((opt) => String(opt.value) === currentValue)
  const selectedDesc = selectedOption?.desc

  const topDescription = control.showDescBottom ? null : description
  const bottomDescription = control.showDescBottom
    ? (selectedDesc || description)
    : null

  return (
    <ControlCard
      title={control.title}
      description={topDescription}
      disabled={disabled}
      disabledReason={disabledReason}
      className="segmented-control"
    >
      <div className="segmented-control-buttons">
        {availableOptions.map((option) => {
          const lines = option.name.split('\n')
          const optionValue = String(option.value)
          return (
            <button
              key={option.value}
              className={`segmented-button ${currentValue === optionValue ? 'active' : ''}`}
              onClick={() => handleSelect(option.value)}
              disabled={disabled}
            >
              {lines.map((line, i) => (
                <span key={`${option.value}-${i}`}>
                  {line}
                  {i < lines.length - 1 && <br />}
                </span>
              ))}
            </button>
          )
        })}
      </div>

      {bottomDescription && (
        <p
          className={`segmented-control-description ${selectedDesc ? 'segmented-control-selected-desc' : ''}`}
          dangerouslySetInnerHTML={{ __html: bottomDescription }}
        />
      )}
    </ControlCard>
  )
}
