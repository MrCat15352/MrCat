import { Box, Button, Section, Flex } from '../components';
import { useBackend } from '../backend';
import { Window } from '../layouts';

export const LocalOrbitalMap = (props, context) => {
  const { act, data } = useBackend(context);
  const {
    map_size = 500,
    ships = [],
    obstacles = [],
    player_ship = null,
  } = data;

  return (
    <Window width={800} height={600}>
      <Window.Content>
        <Flex height="100%">
          <Flex.Item grow>
            <Section fill title="Локальная орбитальная карта">
              <Box
                style={{
                  position: 'relative',
                  width: '100%',
                  height: '400px',
                  background: '#0a0a0a',
                  border: '2px solid #00ffff',
                }}>
                <svg
                  viewBox={`0 0 ${map_size} ${map_size}`}
                  style={{
                    width: '100%',
                    height: '100%',
                  }}>
                  
                  {/* Grid */}
                  <defs>
                    <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                      <rect width="50" height="50" fill="#001122" />
                      <path fill="none" stroke="#003366" strokeWidth="1" d="M 50 0 L 0 0 0 50" />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                  
                  {/* Obstacles */}
                  {obstacles.map((obstacle, index) => (
                    <circle
                      key={index}
                      cx={obstacle.x}
                      cy={obstacle.y}
                      r={obstacle.size}
                      fill="#8B4513"
                      stroke="#A0522D"
                      strokeWidth="2" />
                  ))}
                  
                  {/* Ships */}
                  {ships.map((ship, index) => (
                    <g key={index}>
                      <polygon
                        points={`${ship.x},${ship.y-10} ${ship.x-8},${ship.y+8} ${ship.x+8},${ship.y+8}`}
                        fill={ship.name === player_ship ? '#00ff00' : '#ff4444'}
                        stroke="#ffffff"
                        strokeWidth="2" />
                      <text
                        x={ship.x}
                        y={ship.y + 25}
                        fill="white"
                        fontSize="12"
                        textAnchor="middle">
                        {ship.name}
                      </text>
                      {/* Velocity vector */}
                      {(ship.vel_x !== 0 || ship.vel_y !== 0) && (
                        <line
                          x1={ship.x}
                          y1={ship.y}
                          x2={ship.x + ship.vel_x * 5}
                          y2={ship.y + ship.vel_y * 5}
                          stroke="#00ff00"
                          strokeWidth="2" />
                      )}
                    </g>
                  ))}
                </svg>
              </Box>
            </Section>
          </Flex.Item>
          
          <Flex.Item width="200px">
            <Section title="Управление">
              <Flex direction="column">
                <Flex.Item>
                  <Button
                    fluid
                    icon="arrow-up"
                    content="Вперед"
                    onClick={() => act('orbital_move', { direction: 1 })} />
                </Flex.Item>
                <Flex>
                  <Flex.Item>
                    <Button
                      icon="arrow-left"
                      content="Лево"
                      onClick={() => act('orbital_move', { direction: 8 })} />
                  </Flex.Item>
                  <Flex.Item>
                    <Button
                      icon="arrow-right"
                      content="Право"
                      onClick={() => act('orbital_move', { direction: 4 })} />
                  </Flex.Item>
                </Flex>
                <Flex.Item>
                  <Button
                    fluid
                    icon="arrow-down"
                    content="Назад"
                    onClick={() => act('orbital_move', { direction: 2 })} />
                </Flex.Item>
                <Flex.Item mt={2}>
                  <Button
                    fluid
                    icon="times"
                    content="Выйти из орбиты"
                    color="red"
                    onClick={() => act('exit_orbital_mode')} />
                </Flex.Item>
              </Flex>
            </Section>
            
            <Section title="Информация">
              <Box>
                <b>Корабли в секторе:</b> {ships.length}
              </Box>
              <Box>
                <b>Препятствия:</b> {obstacles.length}
              </Box>
              {player_ship && (
                <Box mt={1}>
                  <b>Ваш корабль:</b> {player_ship}
                </Box>
              )}
            </Section>
          </Flex.Item>
        </Flex>
      </Window.Content>
    </Window>
  );
};