/**
 * @file
 * @author Original by ArcaneMusic (https://github.com/ArcaneMusic)
 * @author Changes Shadowh4nD/jlsnow301
 * @license MIT
 */

import { useLocalState } from '../backend';
import {
  BlockQuote,
  Box,
  Button,
  Divider,
  Image,
  LabeledList,
  Modal,
  Section,
  Stack,
  Tabs,
  TextArea,
} from '../components';
import { decodeHtmlEntities } from 'common/string';

import { useBackend, useSharedState } from '../backend';
import { Window } from '../layouts';

const CENSOR_MESSAGE =
  'Этот канал был признан угрожающим \
  благополучию станции и помечен D-уведомлением Nanotrasen.';

export const Newscaster = (props) => {
  const { act, data } = useBackend();
  return (
    <>
      <NewscasterChannelCreation />
      <NewscasterCommentCreation />
      <NewscasterWantedScreen />
      <NewscasterContent />
    </>
  );
};

/** The modal menu that contains the prompts to making new channels. */
const NewscasterChannelCreation = (props) => {
  const { act, data } = useBackend();
  const [lockedmode, setLockedmode] = useLocalState('lockedmode', true);
  const { creating_channel, name, desc } = data;
  if (!creating_channel) {
    return null;
  }

  return (
    <Modal textAlign="center" mr={1.5}>
      <Stack vertical>
        <>
          <Stack.Item>
            <Box pb={1}>
              Введите название канала:
              <Button
                color="red"
                icon="times"
                position="relative"
                top="20%"
                left="15%"
                onClick={() => act('cancelCreation')}
              />
            </Box>
            <TextArea
              fluid
              height="40px"
              width="240px"
              backgroundColor="black"
              textColor="white"
              maxLength={42}
              onChange={(e, name) =>
                act('setChannelName', {
                  channeltext: name,
                })
              }
            >
              Название канала
            </TextArea>
          </Stack.Item>
          <Stack.Item>
            <Box pb={1}>Введите описание канала:</Box>
            <TextArea
              fluid
              height="150px"
              width="240px"
              backgroundColor="black"
              textColor="white"
              maxLength={512}
              onChange={(e, desc) =>
                act('setChannelDesc', {
                  channeldesc: desc,
                })
              }
            >
              Описание канала
            </TextArea>
          </Stack.Item>
          <Stack.Item>
            <Section>
              Установить канал как публичный или приватный
              <Box pt={1}>
                <Button
                  selected={!lockedmode}
                  onClick={() => setLockedmode(false)}
                >
                  Публичный
                </Button>
                <Button
                  selected={!!lockedmode}
                  onClick={() => setLockedmode(true)}
                >
                  Приватный
                </Button>
              </Box>
            </Section>
          </Stack.Item>
          <Stack.Item>
            <Box>
              <Button
                onClick={() =>
                  act('createChannel', {
                    lockedmode: lockedmode,
                  })
                }
              >
                Создать канал
              </Button>
            </Box>
          </Stack.Item>
        </>
      </Stack>
    </Modal>
  );
};

/** The modal menu that contains the prompts to making new comments. */
const NewscasterCommentCreation = (props) => {
  const { act, data } = useBackend();
  const { creating_comment, viewing_message } = data;
  if (!creating_comment) {
    return null;
  }
  return (
    <Modal textAlign="center" mr={1.5}>
      <Stack vertical>
        <Stack.Item>
          <Box pb={1}>
            Введите комментарий:
            <Button
              color="red"
              position="relative"
              icon="times"
              top="20%"
              left="25%"
              onClick={() => act('cancelCreation')}
            />
          </Box>
          <TextArea
            fluid
            height="120px"
            width="240px"
            backgroundColor="black"
            textColor="white"
            maxLength={512}
            onChange={(e, comment) =>
              act('setCommentBody', {
                commenttext: comment,
              })
            }
          >
            Комментарий
          </TextArea>
        </Stack.Item>
        <Stack.Item>
          <Box>
            <Button
              onClick={() =>
                act('createComment', {
                  messageID: viewing_message,
                })
              }
            >
              Отправить комментарий
            </Button>
          </Box>
        </Stack.Item>
      </Stack>
    </Modal>
  );
};

const NewscasterWantedScreen = (props) => {
  const { act, data } = useBackend();
  const {
    viewing_wanted,
    photo_data,
    security_mode,
    wanted = [],
    criminal_name,
    crime_description,
  } = data;
  if (!viewing_wanted) {
    return null;
  }
  return (
    <Modal textAlign="center" mr={1} width={25}>
      {wanted.map((activeWanted) => (
        <>
          <Stack vertical>
            <Stack.Item>
              <Box bold color="red">
                {activeWanted.active
                  ? 'Активный розыск:'
                  : 'Отклоненный розыск:'}
                <Button
                  color="red"
                  position="relative"
                  icon="times"
                  top="20%"
                  left="15%"
                  onClick={() => act('cancelCreation')}
                />
              </Box>
              {!!activeWanted.criminal && (
                <>
                  <Section>
                    <Box bold>{activeWanted.criminal}</Box>
                    <Box italic>{activeWanted.crime}</Box>
                  </Section>
                  <Image src={activeWanted.image ? activeWanted.image : null} />
                  <Box italic>
                    Опубликовано{' '}
                    {activeWanted.author ? activeWanted.author : 'Н/Д'}
                  </Box>
                </>
              )}
            </Stack.Item>
          </Stack>
          <Divider />
        </>
      ))}
      {security_mode ? (
        <>
          <LabeledList>
            <LabeledList.Item label="Имя преступника">
              <Button
                disabled={!security_mode}
                icon="pen"
                onClick={() => act('setCriminalName')}
              >
                {criminal_name ? criminal_name : ' Н/Д'}
              </Button>
            </LabeledList.Item>
            <LabeledList.Item label="Преступная деятельность">
              <Button
                nowrap={false}
                disabled={!security_mode}
                icon="pen"
                onClick={() => act('setCrimeData')}
              >
                {crime_description ? crime_description : ' Н/Д'}
              </Button>
            </LabeledList.Item>
          </LabeledList>
          <Section>
            <Button
              icon="camera"
              selected={photo_data}
              disabled={!security_mode}
              onClick={() => act('togglePhoto')}
            >
              {photo_data ? 'Удалить фото' : 'Прикрепить фото'}
            </Button>
            <Button
              disabled={!security_mode}
              icon="volume-up"
              onClick={() => act('submitWantedIssue')}
            >
              Объявить в розыск
            </Button>
            <Button
              disabled={!security_mode}
              icon="times"
              color="red"
              onClick={() => act('clearWantedIssue')}
            >
              Снять с розыска
            </Button>
          </Section>
        </>
      ) : (
        <Box>
          {wanted.map((activeWanted) =>
            activeWanted.active
              ? 'Пожалуйста, обратитесь к местному офицеру безопасности при обнаружении.'
              : 'Розыск не объявлен. Хорошего дня.',
          )}
        </Box>
      )}
    </Modal>
  );
};

const NewscasterContent = (props) => {
  const { act, data } = useBackend();
  const { current_channel = {} } = data;
  return (
    <Stack fill vertical>
      <Stack.Item grow>
        <Stack fill>
          <Stack.Item grow>
            <NewscasterChannelSelector />
          </Stack.Item>
          <Stack.Item grow={2}>
            <Stack fill vertical>
              <Stack.Item grow>
                <NewscasterChannelBox
                  channelName={current_channel.name}
                  channelOwner={current_channel.owner}
                  channelDesc={current_channel.desc}
                />
              </Stack.Item>
            </Stack>
          </Stack.Item>
        </Stack>
      </Stack.Item>
      <Stack.Item grow>
        <NewscasterChannelMessages />
      </Stack.Item>
    </Stack>
  );
};

/** The Channel Box is the basic channel information where buttons live.*/
const NewscasterChannelBox = (props) => {
  const { act, data } = useBackend();
  const {
    channelName,
    channelDesc,
    channelLocked,
    channelAuthor,
    channelCensored,
    viewing_channel,
    admin_mode,
    photo_data,
    paper,
    user,
  } = data;
  return (
    <Section fill title={channelName}>
      <Stack fill vertical>
        <Stack.Item grow>
          {channelCensored ? (
            <Section>
              <BlockQuote color="red">
                <b>ВНИМАНИЕ:</b> {CENSOR_MESSAGE}
              </BlockQuote>
            </Section>
          ) : (
            <Section fill scrollable>
              <BlockQuote italic fontSize={1.2} wrap>
                {decodeHtmlEntities(channelDesc)}
              </BlockQuote>
            </Section>
          )}
        </Stack.Item>
        <Stack.Item>
          <Box>
            <Button
              icon="print"
              disabled={
                (channelLocked && channelAuthor !== user.name) ||
                channelCensored
              }
              onClick={() => act('createStory', { current: viewing_channel })}
              mt={1}
            >
              Опубликовать новость
            </Button>
            <Button
              icon="camera"
              selected={photo_data}
              disabled={
                (channelLocked && channelAuthor !== user.name) ||
                channelCensored
              }
              onClick={() => act('togglePhoto')}
            >
              Выбрать фото
            </Button>
            {!!admin_mode && (
              <Button
                icon="ban"
                tooltip="Заблокировать весь канал и его \
                  содержимое как опасное для станции. Нельзя отменить."
                disabled={!admin_mode || !viewing_channel}
                onClick={() =>
                  act('channelDNotice', {
                    secure: admin_mode,
                    channel: viewing_channel,
                  })
                }
              >
                D-уведомление
              </Button>
            )}
          </Box>
          <Box>
            <Button
              icon="newspaper"
              tooltip={paper <= 0 ? 'Сначала вставьте бумагу!' : ''}
              disabled={paper <= 0}
              onClick={() => act('printNewspaper')}
            >
              Печать газеты
            </Button>
          </Box>
        </Stack.Item>
      </Stack>
    </Section>
  );
};

/** Channel select is the left-hand menu where all the channels are listed. */
const NewscasterChannelSelector = (props) => {
  const { act, data } = useBackend();
  const { channels = [], viewing_channel, wanted = [] } = data;
  return (
    <Section minHeight="100%" width={window.innerWidth - 410 + 'px'}>
      <Tabs vertical>
        {wanted.map((activeWanted) => (
          <Tabs.Tab
            pt={0.75}
            pb={0.75}
            mr={1}
            key={activeWanted.index}
            icon={activeWanted.active ? 'skull-crossbones' : null}
            textColor={activeWanted.active ? 'red' : 'grey'}
            onClick={() => act('toggleWanted')}
          >
            Розыск
          </Tabs.Tab>
        ))}
        {channels.map((channel) => (
          <Tabs.Tab
            key={channel.index}
            pt={0.75}
            pb={0.75}
            mr={1}
            selected={viewing_channel === channel.ID}
            icon={channel.censored ? 'ban' : null}
            textColor={channel.censored ? 'red' : 'white'}
            onClick={() =>
              act('setChannel', {
                channel: channel.ID,
              })
            }
          >
            {channel.name}
          </Tabs.Tab>
        ))}
        <Tabs.Tab
          pt={0.75}
          pb={0.75}
          mr={1}
          textColor="white"
          color="Green"
          onClick={() => act('startCreateChannel')}
        >
          Создать канал [+]
        </Tabs.Tab>
      </Tabs>
    </Section>
  );
};

/** This is where the channels comments get spangled out (tm) */
const NewscasterChannelMessages = (props) => {
  const { act, data } = useBackend();
  const {
    messages = [],
    viewing_channel,
    admin_mode,
    channelCensored,
    channelLocked,
    channelAuthor,
    user,
  } = data;
  if (channelCensored) {
    return (
      <Section color="red">
        <b>ВНИМАНИЕ:</b> Комментарии не могут быть прочитаны в данный момент.
        <br />
        Спасибо за понимание и хорошего дня.
      </Section>
    );
  }
  const visibleMessages = messages.filter(
    (message) => message.ID !== viewing_channel,
  );
  return (
    <Section>
      {visibleMessages.map((message) => {
        return (
          <Section
            key={message.index}
            textColor="white"
            title={
              <i>
                {message.censored_author ? (
                  <Box textColor="red">
                    От: [УДАЛЕНО]. <b>D-уведомление</b> .
                  </Box>
                ) : (
                  <>
                    От: {message.auth} в {message.time}
                  </>
                )}
              </i>
            }
            buttons={
              <>
                {!!admin_mode && (
                  <Button
                    icon="comment-slash"
                    tooltip="Заблокировать новость"
                    disabled={!admin_mode}
                    onClick={() =>
                      act('storyCensor', {
                        messageID: message.ID,
                      })
                    }
                  />
                )}
                {!!admin_mode && (
                  <Button
                    icon="user-slash"
                    tooltip="Заблокировать автора"
                    disabled={!admin_mode}
                    onClick={() =>
                      act('authorCensor', {
                        messageID: message.ID,
                      })
                    }
                  />
                )}
                <Button
                  icon="comment"
                  tooltip="Оставить комментарий."
                  disabled={
                    message.censored_author ||
                    message.censored_message ||
                    user.name === 'Unknown' ||
                    (!!channelLocked && channelAuthor !== user.name)
                  }
                  onClick={() =>
                    act('startComment', {
                      messageID: message.ID,
                    })
                  }
                />
              </>
            }
          >
            <BlockQuote>
              {message.censored_message ? (
                <Section textColor="red">
                  Это сообщение было признано опасным для общего благополучия
                  станции и поэтому помечено <b>D-уведомлением</b>.
                </Section>
              ) : (
                <Section pl={1}>
                  <Box>{message.body}</Box>
                </Section>
              )}
              {message.photo !== null && !message.censored_message && (
                <Image src={message.photo} />
              )}
              {!!message.comments && (
                <Box>
                  {message.comments.map((comment) => (
                    <BlockQuote key={comment.index}>
                      <Box italic textColor="white">
                        От: {comment.auth} в {comment.time}
                      </Box>
                      <Section ml={2.5}>
                        <Box>{comment.body}</Box>
                      </Section>
                    </BlockQuote>
                  ))}
                </Box>
              )}
            </BlockQuote>
            <Divider />
          </Section>
        );
      })}
    </Section>
  );
};