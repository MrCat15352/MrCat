import { useBackend } from '../backend';
import { Box, Button, Section } from '../components';
import { Window } from '../layouts';

export const LocalOrbitalMap = (props, context) => {
  const { act, data } = useBackend(context);

  return (
    <Window width={600} height={400}>
      <Window.Content>
        <Section title="Локальная орбитальная карта">
          <Box>
            Карта размером: {data.map_size || 500}x{data.map_size || 500}
          </Box>
          <Box>
            Кораблей в секторе: {data.ships ? data.ships.length : 0}
          </Box>
          <Box>
            Препятствий: {data.obstacles ? data.obstacles.length : 0}
          </Box>
          <Button
            content="Выйти из орбиты"
            color="red"
            onClick={() => act('exit_orbital_mode')}
          />
          <Button
            content="Тест движения"
            onClick={() => act('orbital_move', { direction: 1 })}
          />
        </Section>
      </Window.Content>
    </Window>
  );
};