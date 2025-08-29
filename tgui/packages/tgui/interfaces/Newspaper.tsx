import { Box, Button, Section } from '../components';
import { Window } from '../layouts';

export const Newspaper = () => {
  return (
    <Window width={300} height={400}>
      <Window.Content backgroundColor="#858387">
        <Section>
          <Box bold fontSize="30px">
            Грифон
          </Box>
          <Box bold fontSize="15px">
            Только для использования на космических объектах!
          </Box>
          <Box>Газета работает!</Box>
        </Section>
      </Window.Content>
    </Window>
  );
};