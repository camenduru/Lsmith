import { css, styled, useTheme } from 'decorock'
import type { RunRequest } from 'internal:api'
import { createSignal} from 'solid-js'
import { createStore } from 'solid-js/store'

import { api } from '~/api'
import { Button } from '~/components/ui/button'
import { Input } from '~/components/ui/input'
import { VStack } from '~/components/ui/stack'

const Container = styled.div`
  display: flex;
  height: 100%;
  justify-content: center;
`

const Setting = styled.div`
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 1rem;
  gap: 0.5rem;

  & > div {
    width: 100%;
  }
`

export const Command = () => {
  const theme = useTheme()
  const [req, setReq] = createStore({
    command: '',
  } as RunRequest)
  const [status, setStatus] = createSignal<Record<string, any> | null>(null)

  return (
    <Container>
      <VStack
        class={css`
          width: 60%;
          ${theme.media.breakpoints.md} {
            width: 100%;
          }

          progress {
            width: 100%;
          }
        `}
      >
        <Setting>
          <div>Run Command</div>
          <Input
            placeholder="cmd"
            value={req.command || ''}
            onChange={(e) => setReq('command', e.currentTarget.value)}
          />
          <Button
            task={async () => {
              const { raw } = await api.runCommandRaw({ runRequest: { ...req } })
              const reader = raw.body?.getReader()
              if (!reader) return
              let done = true
              while (done) {
                const res = await reader.read()
                done = !res.done
                try {
                  setStatus(JSON.parse(new TextDecoder().decode(res.value) || ''))
                } catch (_) {}
              }
              setStatus(null)
            }}
          >
            Run Command
          </Button>
        </Setting>

      </VStack>
    </Container>
  )
}
