import { useBackend } from '../backend';
import { Box, Button, Section } from '../components';
import { Window } from '../layouts';

export const TestLocalMap = (props, context) => {
  const { act, data } = useBackend(context);

  return (
    <Window width={400} height={300}>
      <Window.Content>
        <Section title="Test Local Map">
          <Box>
            This is a test interface to verify TGUI is working.
          </Box>
          <Button
            content="Test Button"
            onClick={() => act('test_action')}
          />
        </Section>
      </Window.Content>
    </Window>
  );
};