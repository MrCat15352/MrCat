import { useBackend } from '../backend';
import { Box, Button, Section, Stack } from '../components';
import { Window } from '../layouts';

export const Newspaper = (props, context) => {
  const { act, data } = useBackend(context);
  const {
    current_page = 0,
    scribble_message = '',
    channels = [],
    channel_data = {},
    wanted_criminal = '',
    wanted_body = '',
    wanted_photo = null,
    pages = 0,
  } = data;

  const renderCover = () => (
    <Section fill>
      {/* Заголовок газеты */}
      <Box
        textAlign="center"
        p={2}
        mb={2}
        style={{
          border: '3px double #000',
          backgroundColor: '#f8f8f8',
        }}
      >
        <Box bold fontSize="28px" mb={1} style={{ fontFamily: 'serif' }}>
          🦅 ГРИФОН 🦅
        </Box>
        <Box fontSize="11px" italic>
          Ежедневная космическая газета • Выпуск #{data.issue_number || 1337}
        </Box>
        <Box fontSize="10px" color="#666">
          Nanotrasen Media Group • Все права защищены
        </Box>
      </Box>

      {/* Главные новости */}
      <Box
        mb={2}
        p={2}
        style={{ border: '1px solid #ccc', backgroundColor: '#fff' }}
      >
        <Box bold fontSize="14px" mb={1} color="red">
          🔥 ГЛАВНЫЕ НОВОСТИ СМЕНЫ
        </Box>
        <Box fontSize="12px" style={{ lineHeight: '1.4' }}>
          {channels.length > 0 ? (
            <>
              {channels[0]?.name && `Эксклюзив от канала "${channels[0].name}"`}
              <Box mt={1} italic>
                Подробности читайте на следующих страницах...
              </Box>
            </>
          ) : (
            <>
              Новости смены: На станции спокойно, все системы работают штатно.
              <Box mt={1} italic>
                Подробности читайте на следующих страницах...
              </Box>
            </>
          )}
        </Box>
      </Box>

      {/* Содержание в виде колонок */}
      <Box style={{ display: 'flex', gap: '10px' }}>
        <Box style={{ flex: 1 }}>
          <Box
            bold
            fontSize="12px"
            mb={1}
            style={{ borderBottom: '2px solid #000' }}
          >
            📰 СОДЕРЖАНИЕ
          </Box>
          {!channels || channels.length === 0 ? (
            <>
              <Box fontSize="10px" mb={1}>Новости смены стр.2</Box>
              <Box fontSize="10px" mb={1}>Медицинские новости стр.3</Box>
              <Box fontSize="10px" mb={1}>Отдел снабжения стр.4</Box>
              <Box fontSize="10px" mb={1}>Реклама стр.5</Box>
            </>
          ) : (
            <>
              {channels.map((channel, index) => (
                <Box
                  key={index}
                  mb={1}
                  style={{ display: 'flex', justifyContent: 'space-between' }}
                >
                  <Box fontSize="10px">{channel.name}</Box>
                  <Box fontSize="10px" bold>
                    стр.{index + 2}
                  </Box>
                </Box>
              ))}
              {wanted_criminal && (
                <Box
                  mb={1}
                  style={{ display: 'flex', justifyContent: 'space-between' }}
                >
                  <Box fontSize="10px" color="red">
                    🚨 РОЗЫСК
                  </Box>
                  <Box fontSize="10px" bold>
                    стр.{pages + 2}
                  </Box>
                </Box>
              )}
            </>
          )}
        </Box>

        <Box style={{ flex: 1 }}>
          <Box
            bold
            fontSize="12px"
            mb={1}
            style={{ borderBottom: '2px solid #000' }}
          >
            📊 СВОДКА ДНЯ
          </Box>
          <Box fontSize="10px" mb={1}>
            📈 Каналов новостей: {channels?.length || 4}
          </Box>
          <Box fontSize="10px" mb={1}>
            📝 Всего статей: {channels?.reduce((sum, ch) => sum + (ch.messages || 1), 0) || 5}
          </Box>
          <Box fontSize="10px" mb={1}>
            {wanted_criminal ? '🚨 Активный розыск' : '✅ Безопасная смена'}
          </Box>
        </Box>
      </Box>

      {scribble_message && current_page === 0 && (
        <Box
          mt={2}
          p={1}
          style={{ border: '1px dashed #999', backgroundColor: '#fffacd' }}
        >
          <Box fontSize="9px" italic>
            ✏️ Заметка читателя: "{scribble_message}"
          </Box>
        </Box>
      )}
    </Section>
  );

  const renderChannel = () => {
    if (!channel_data || !channel_data.name) {
      return (
        <Section fill>
          <Box textAlign="center" p={4}>
            <Box fontSize="16px" mb={2}>📰</Box>
            <Box>Страница {current_page + 1}</Box>
            <Box italic>Загрузка контента...</Box>
          </Box>
        </Section>
      );
    }

    return (
      <Section fill>
        {/* Заголовок канала */}
        <Box
          p={2}
          mb={2}
          style={{
            border: '2px solid #000',
            backgroundColor: '#f0f8ff',
            borderRadius: '5px',
          }}
        >
          <Box bold fontSize="18px" mb={1} style={{ fontFamily: 'serif' }}>
            📺 {channel_data.name.toUpperCase()}
          </Box>
          <Box fontSize="10px" italic color="#666">
            Редактор: {channel_data.author} • Канал #{current_page}
          </Box>
        </Box>

        {channel_data.censored ? (
          <Box
            p={2}
            color="red"
            style={{
              border: '2px solid red',
              backgroundColor: '#ffe6e6',
              textAlign: 'center',
            }}
          >
            <Box bold fontSize="14px" mb={1}>
              ⚠️ ЦЕНЗУРА ⚠️
            </Box>
            <Box fontSize="11px">
              Канал заблокирован по решению администрации станции. Содержимое не
              допущено к публикации.
            </Box>
          </Box>
        ) : (
          <>
            {!channel_data.messages || channel_data.messages.length === 0 ? (
              <Box
                textAlign="center"
                italic
                p={3}
                style={{
                  backgroundColor: '#f9f9f9',
                  border: '1px dashed #ccc',
                }}
              >
                📭 В этом канале пока нет публикаций
              </Box>
            ) : (
              channel_data.messages.map((message, index) => (
                <Box
                  key={index}
                  mb={3}
                  p={2}
                  style={{
                    border: '1px solid #ddd',
                    backgroundColor: index % 2 === 0 ? '#fff' : '#fafafa',
                    borderRadius: '3px',
                  }}
                >
                  {/* Заголовок статьи */}
                  <Box
                    bold
                    fontSize="13px"
                    mb={1}
                    style={{
                      borderBottom: '1px solid #eee',
                      paddingBottom: '5px',
                    }}
                  >
                    📄 Статья #{index + 1}
                  </Box>

                  {/* Текст статьи */}
                  <Box
                    mb={2}
                    fontSize="11px"
                    style={{ lineHeight: '1.5', textAlign: 'justify' }}
                  >
                    {message.body}
                  </Box>

                  {/* Изображение */}
                  {message.img && (
                    <Box textAlign="center" mb={2}>
                      <img
                        src={message.img}
                        width="160"
                        style={{
                          maxWidth: '160px',
                          border: '1px solid #ccc',
                          borderRadius: '3px',
                        }}
                      />
                    </Box>
                  )}

                  {/* Подпись */}
                  <Box
                    fontSize="9px"
                    italic
                    textAlign="right"
                    style={{ borderTop: '1px dotted #ccc', paddingTop: '5px' }}
                  >
                    ✍️ {message.author} • {message.time}
                  </Box>
                </Box>
              ))
            )}
          </>
        )}

        {scribble_message && current_page > 0 && current_page <= pages && (
          <Box
            mt={2}
            p={1}
            style={{ border: '1px dashed #999', backgroundColor: '#fffacd' }}
          >
            <Box fontSize="9px" italic>
              ✏️ Заметка читателя: "{scribble_message}"
            </Box>
          </Box>
        )}
      </Section>
    );
  };

  const renderWanted = () => (
    <Section fill>
      {wanted_criminal ? (
        <>
          {/* Заголовок розыска */}
          <Box
            textAlign="center"
            p={2}
            mb={3}
            style={{
              border: '3px solid red',
              backgroundColor: '#ffebee',
              borderRadius: '5px',
            }}
          >
            <Box bold fontSize="20px" color="red" mb={1}>
              🚨 ВНИМАНИЕ! РОЗЫСК! 🚨
            </Box>
            <Box fontSize="12px" bold>
              СЛУЖБА БЕЗОПАСНОСТИ СТАНЦИИ
            </Box>
          </Box>

          {/* Карточка преступника */}
          <Box
            style={{
              display: 'flex',
              gap: '15px',
              border: '2px solid #d32f2f',
              padding: '15px',
              backgroundColor: '#fff',
            }}
          >
            {/* Фото */}
            <Box style={{ flex: '0 0 120px' }}>
              {wanted_photo ? (
                <Box textAlign="center">
                  <img
                    src={wanted_photo}
                    width="120"
                    style={{
                      maxWidth: '120px',
                      border: '2px solid #000',
                      borderRadius: '3px',
                    }}
                  />
                  <Box fontSize="8px" mt={1}>
                    ФОТО ПОДОЗРЕВАЕМОГО
                  </Box>
                </Box>
              ) : (
                <Box
                  textAlign="center"
                  style={{
                    width: '120px',
                    height: '120px',
                    border: '2px dashed #ccc',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: '#f5f5f5',
                  }}
                >
                  <Box fontSize="10px" color="#666">
                    ФОТО
                    <br />
                    НЕ
                    <br />
                    ПРЕДОСТАВЛЕНО
                  </Box>
                </Box>
              )}
            </Box>

            {/* Информация */}
            <Box style={{ flex: 1 }}>
              <Box mb={2}>
                <Box bold fontSize="12px" color="red" mb={1}>
                  👤 ИМЯ ПОДОЗРЕВАЕМОГО:
                </Box>
                <Box
                  bold
                  fontSize="16px"
                  p={1}
                  style={{
                    border: '1px solid #000',
                    backgroundColor: '#ffcdd2',
                  }}
                >
                  {wanted_criminal.toUpperCase()}
                </Box>
              </Box>

              <Box mb={2}>
                <Box bold fontSize="12px" color="red" mb={1}>
                  ⚖️ ОБВИНЕНИЯ:
                </Box>
                <Box
                  fontSize="11px"
                  p={2}
                  style={{
                    border: '1px solid #ccc',
                    backgroundColor: '#fff',
                    lineHeight: '1.4',
                    minHeight: '60px',
                  }}
                >
                  {wanted_body}
                </Box>
              </Box>

              <Box
                textAlign="center"
                p={1}
                style={{
                  border: '2px solid #ff5722',
                  backgroundColor: '#fff3e0',
                  borderRadius: '3px',
                }}
              >
                <Box bold fontSize="10px" color="#d84315">
                  ⚠️ ПРИ ОБНАРУЖЕНИИ НЕМЕДЛЕННО СООБЩИТЕ В СЛУЖБУ БЕЗОПАСНОСТИ
                  ⚠️
                </Box>
              </Box>
            </Box>
          </Box>
        </>
      ) : (
        <Box
          textAlign="center"
          p={4}
          style={{
            border: '1px dashed #ccc',
            backgroundColor: '#f9f9f9',
          }}
        >
          <Box fontSize="14px" mb={2}>
            📰
          </Box>
          <Box italic fontSize="11px">
            На данный момент активных розысков нет.
            <br />
            Остальное место занимают рекламные объявления.
          </Box>
        </Box>
      )}

      {scribble_message && current_page === pages + 1 && (
        <Box
          mt={2}
          p={1}
          style={{ border: '1px dashed #999', backgroundColor: '#fffacd' }}
        >
          <Box fontSize="9px" italic>
            ✏️ Заметка читателя: "{scribble_message}"
          </Box>
        </Box>
      )}
    </Section>
  );

  const getCurrentContent = () => {
    if (current_page === 0) return renderCover();
    
    // Если есть розыск и это последняя страница
    if (wanted_criminal && current_page > pages) {
      return renderWanted();
    }
    
    // Обычные страницы каналов
    return renderChannel();
  };

  return (
    <Window width={500} height={650}>
      <Window.Content
        style={{
          backgroundColor: '#f5f5dc',
          backgroundImage:
            'linear-gradient(45deg, #f5f5dc 25%, transparent 25%), linear-gradient(-45deg, #f5f5dc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f5f5dc 75%), linear-gradient(-45deg, transparent 75%, #f5f5dc 75%)',
          backgroundSize: '20px 20px',
          backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px',
        }}
      >
        <Stack fill vertical>
          <Stack.Item grow>
            <Box
              p={2}
              style={{
                backgroundColor: '#fff',
                border: '2px solid #8b4513',
                borderRadius: '5px',
                boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                minHeight: '550px',
              }}
            >
              {getCurrentContent()}
            </Box>
          </Stack.Item>

          <Stack.Item>
            <Box
              p={1}
              style={{
                backgroundColor: '#8b4513',
                borderRadius: '3px',
                margin: '5px 0',
              }}
            >
              <Stack>
                <Stack.Item grow>
                  {current_page > 0 && (
                    <Button
                      icon="chevron-left"
                      color="brown"
                      onClick={() => act('prev_page')}
                    >
                      ← Назад
                    </Button>
                  )}
                </Stack.Item>

                <Stack.Item>
                  <Box
                    textAlign="center"
                    bold
                    color="white"
                    style={{
                      backgroundColor: '#654321',
                      padding: '5px 15px',
                      borderRadius: '15px',
                      minWidth: '60px',
                    }}
                  >
                    Стр. {current_page + 1}
                  </Box>
                </Stack.Item>

                <Stack.Item grow>
                  <Box textAlign="right">
                    {(current_page === 0 || (current_page > 0 && channel_data && channel_data.name) || (wanted_criminal && current_page <= pages)) && (
                      <Button
                        icon="chevron-right"
                        color="brown"
                        onClick={() => act('next_page')}
                      >
                        Вперед →
                      </Button>
                    )}
                  </Box>
                </Stack.Item>
              </Stack>
            </Box>
          </Stack.Item>
        </Stack>
      </Window.Content>
    </Window>
  );
};
