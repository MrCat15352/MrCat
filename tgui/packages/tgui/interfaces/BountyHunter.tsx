import { useLocalState, useBackend } from '../backend';
import {
  Box,
  Button,
  Flex,
  Input,
  LabeledList,
  NumberInput,
  Section,
  Stack,
  Table,
  Tabs,
  TextArea,
} from '../components';
import { Window } from '../layouts';

type BountyEntry = {
  id: string;
  targetName: string;
  targetFaction: string;
  status: string;
  reason: string;
  reward: number;
  clientName: string;
  clientFaction: string;
  timeAgo: string;
};

type Data = {
  mode: string;
  hasCard: boolean;
  cardName: string;
  cardFaction: string;
  bountyEntries: BountyEntry[];
};

export const BountyHunter = (props, context) => {
  const { act, data } = useBackend(context);
  const { mode, hasCard, cardName, cardFaction, bountyEntries } = data;

  return (
    <Window width={900} height={700}>
      <Window.Content>
        <Stack fill vertical>
          <Stack.Item>
            <Section title="Авторизация">
              <Flex>
                <Flex.Item grow>
                  {hasCard ? (
                    <Box fontSize="14px">
                      <Box color="good">✓ Карта вставлена</Box>
                      <Box>Имя: {cardName || 'Неизвестно'}</Box>
                      <Box>Фракция: {cardFaction || 'Неизвестно'}</Box>
                    </Box>
                  ) : (
                    <Box color="bad" fontSize="14px">Вставьте ID карту для авторизации</Box>
                  )}
                </Flex.Item>
                <Flex.Item>
                  {hasCard && (
                    <Button
                      icon="eject"
                      content="Извлечь карту"
                      onClick={() => act('ejectCard')}
                    />
                  )}
                </Flex.Item>
              </Flex>
            </Section>
          </Stack.Item>

          <Stack.Item grow>
            <Tabs>
              <Tabs.Tab
                selected={mode === 'view'}
                onClick={() => act('setMode', { mode: 'view' })}
              >
                Просмотр заявок
              </Tabs.Tab>
              <Tabs.Tab
                selected={mode === 'create'}
                onClick={() => act('setMode', { mode: 'create' })}
                disabled={!hasCard}
              >
                Создать заявку
              </Tabs.Tab>
            </Tabs>

            {mode === 'view' ? (
              <BountyList bountyEntries={bountyEntries} hasCard={hasCard} />
            ) : (
              <CreateBounty hasCard={hasCard} />
            )}
          </Stack.Item>
        </Stack>
      </Window.Content>
    </Window>
  );
};

const BountyList = (props, context) => {
  const { bountyEntries, hasCard } = props;
  const { act } = useBackend(context);

  return (
    <Section title="Активные заявки" fill scrollable>
      {bountyEntries.length === 0 ? (
        <Box textAlign="center" color="average" mt={4} fontSize="14px">
          Нет активных заявок
        </Box>
      ) : (
        <Table>
          <Table.Row header>
            <Table.Cell fontSize="14px">Цель</Table.Cell>
            <Table.Cell fontSize="14px">Фракция</Table.Cell>
            <Table.Cell fontSize="14px">Статус</Table.Cell>
            <Table.Cell fontSize="14px">Награда</Table.Cell>
            <Table.Cell fontSize="14px">Заказчик</Table.Cell>
            <Table.Cell fontSize="14px">Время</Table.Cell>
            <Table.Cell fontSize="14px">Действия</Table.Cell>
          </Table.Row>
          {bountyEntries.map((entry) => (
            <Table.Row key={entry.id}>
              <Table.Cell>
                <Box bold fontSize="14px">{entry.targetName}</Box>
                <Box fontSize="12px" color="average">
                  {entry.reason}
                </Box>
              </Table.Cell>
              <Table.Cell fontSize="14px">{entry.targetFaction || 'Неизвестно'}</Table.Cell>
              <Table.Cell>
                <Box
                  fontSize="14px"
                  color={
                    entry.status === 'Живым'
                      ? 'good'
                      : entry.status === 'Мёртвым'
                        ? 'bad'
                        : 'average'
                  }
                >
                  {entry.status}
                </Box>
              </Table.Cell>
              <Table.Cell>
                <Box color="good" bold fontSize="14px">
                  {entry.reward} кр.
                </Box>
              </Table.Cell>
              <Table.Cell>
                <Box fontSize="14px">{entry.clientName}</Box>
                <Box fontSize="12px" color="average">
                  {entry.clientFaction}
                </Box>
              </Table.Cell>
              <Table.Cell fontSize="14px">{entry.timeAgo}</Table.Cell>
              <Table.Cell>
                {hasCard && (
                  <Button
                    icon="trash"
                    color="bad"
                    content="Отменить"
                    onClick={() =>
                      act('removeBounty', { entryId: entry.id })
                    }
                  />
                )}
              </Table.Cell>
            </Table.Row>
          ))}
        </Table>
      )}
    </Section>
  );
};

const CreateBounty = (props, context) => {
  const { hasCard } = props;
  const { act } = useBackend(context);
  const [targetName, setTargetName] = useLocalState(context, 'targetName', '');
  const [targetFaction, setTargetFaction] = useLocalState(context, 'targetFaction', '');
  const [targetStatus, setTargetStatus] = useLocalState(context, 'targetStatus', 'Живым или мёртвым');
  const [reason, setReason] = useLocalState(context, 'reason', '');
  const [reward, setReward] = useLocalState(context, 'reward', 1000);

  const handleSubmit = () => {
    if (!targetName || !reason || reward <= 0) {
      return;
    }

    act('createBounty', {
      targetName,
      targetFaction,
      targetStatus,
      reason,
      reward,
    });

    // Сброс формы
    setTargetName('');
    setTargetFaction('');
    setTargetStatus('Живым или мёртвым');
    setReason('');
    setReward(1000);
  };

  if (!hasCard) {
    return (
      <Section title="Создание заявки" fill>
        <Box textAlign="center" color="bad" mt={4} fontSize="14px">
          Для создания заявки необходимо вставить ID карту
        </Box>
      </Section>
    );
  }

  return (
    <Section title="Создание заявки" fill>
      <Stack vertical>
        <Stack.Item>
          <LabeledList>
            <LabeledList.Item label="Имя цели">
              <Input
                placeholder="Введите имя цели"
                value={targetName}
                onChange={(e, value) => setTargetName(value)}
                width="100%"
                fontSize="14px"
              />
            </LabeledList.Item>
            <LabeledList.Item label="Фракция цели">
              <Input
                placeholder="Фракция цели (необязательно)"
                value={targetFaction}
                onChange={(e, value) => setTargetFaction(value)}
                width="100%"
                fontSize="14px"
              />
            </LabeledList.Item>
            <LabeledList.Item label="Статус">
              <Button.Checkbox
                checked={targetStatus === 'Живым'}
                onClick={() => setTargetStatus('Живым')}
              >
                Живым
              </Button.Checkbox>
              <Button.Checkbox
                checked={targetStatus === 'Мёртвым'}
                onClick={() => setTargetStatus('Мёртвым')}
              >
                Мёртвым
              </Button.Checkbox>
              <Button.Checkbox
                checked={targetStatus === 'Живым или мёртвым'}
                onClick={() => setTargetStatus('Живым или мёртвым')}
              >
                Живым или мёртвым
              </Button.Checkbox>
            </LabeledList.Item>
            <LabeledList.Item label="Награда (кредиты)">
              <Input
                value={reward}
                onChange={(e, value) => {
                  const num = parseInt(value) || 1;
                  if (num >= 1 && num <= 999999) {
                    setReward(num);
                  }
                }}
                width="200px"
              />
            </LabeledList.Item>
          </LabeledList>
        </Stack.Item>
        
        <Stack.Item>
          <Box mb={1} fontSize="14px">Причина розыска:</Box>
          <TextArea
            placeholder="Опишите причину розыска..."
            value={reason}
            onChange={(e, value) => setReason(value)}
            height="100px"
            width="100%"
            fontSize="14px"
          />
        </Stack.Item>
        
        <Stack.Item>
          <Flex justify="space-between">
            <Flex.Item>
              <Box color="average" fontSize="14px">
                Деньги будут списаны с вашего счёта при создании заявки
              </Box>
            </Flex.Item>
            <Flex.Item>
              <Button
                icon="plus"
                content="Создать заявку"
                color="good"
                disabled={!targetName || !reason || reward <= 0}
                onClick={handleSubmit}
              />
            </Flex.Item>
          </Flex>
        </Stack.Item>
      </Stack>
    </Section>
  );
};