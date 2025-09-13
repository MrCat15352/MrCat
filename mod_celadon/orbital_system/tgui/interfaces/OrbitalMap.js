import { Box, Button, Section, Table, DraggableClickableControl, Dropdown, Divider, NoticeBox, ProgressBar, Flex } from '../../../tgui/packages/tgui/components';
import { useBackend, useLocalState } from '../../../tgui/packages/tgui/backend';
import { Window } from '../../../tgui/packages/tgui/layouts';
import { Component } from 'inferno';

export const OrbitalMap = (props, context) => {
  const { act, data } = useBackend(context);
  const {
    map_objects = [],
    update_index = 0,
  } = data;
  const [
    zoomScale,
    setZoomScale,
  ] = useLocalState(context, 'zoomScale', 1);
  const [
    xOffset,
    setXOffset,
  ] = useLocalState(context, 'xOffset', 0);
  const [
    yOffset,
    setYOffset,
  ] = useLocalState(context, 'yOffset', 0);
  const [
    trackedBody,
    setTrackedBody,
  ] = useLocalState(context, 'trackedBody', 'None');

  let dynamicXOffset = xOffset;
  let dynamicYOffset = yOffset;

  let trackedObject = null;
  if (map_objects.length > 0) {
    // Find the right tracked body
    map_objects.forEach(element => {
      if (element.name === trackedBody && !trackedObject) {
        trackedObject = element;
        if (trackedBody !== 'None') {
          dynamicXOffset = trackedObject.position_x + trackedObject.velocity_x;
          dynamicYOffset = trackedObject.position_y + trackedObject.velocity_y;
        }
      }
    });
  }

  return (
    <Window
      width={1136}
      height={770}>
      <Window.Content fitted>
        <Flex height="100%">
          <Flex.Item class="OrbitalMap__crutch OrbitalMap__radar" grow id="radar">
            <OrbitalMapDisplay
              dynamicXOffset={dynamicXOffset}
              dynamicYOffset={dynamicYOffset}
              isTracking={trackedBody !== "None"}
              zoomScale={zoomScale}
              setZoomScale={setZoomScale}
              setXOffset={setXOffset}
              setYOffset={setYOffset}
              setTrackedBody={setTrackedBody}
              trackedObject={trackedObject} />
          </Flex.Item>
          <Flex.Item class="OrbitalMap__panel">
            <Section fill scrollable>
              <Section title="Отслеживание тел">
                <Box bold>
                  Отслеживание
                </Box>
                <Box mb={1}>
                  {trackedBody}
                </Box>
                <Box>
                  <b>
                    X:&nbsp;
                  </b>
                  {trackedObject && trackedObject.position_x}
                </Box>
                <Box>
                  <b>
                    Y:&nbsp;
                  </b>
                  {trackedObject && trackedObject.position_y}
                </Box>
                <Box>
                  <b>
                    Ускорение:&nbsp;
                  </b>
                  ({trackedObject && trackedObject.velocity_x}
                  , {trackedObject && trackedObject.velocity_y})
                </Box>
                <Box>
                  <b>
                    Радиус:&nbsp;
                  </b>
                  {trackedObject && trackedObject.radius} БСЕ
                </Box>
                <Divider />
                <Dropdown
                  selected={trackedBody}
                  width="100%"
                  color="grey"
                  options={['None'].concat(map_objects.sort((first, second) => { 
                    return second.priority - first.priority; 
                  }).map(map_object => (map_object.name)))}
                  onSelected={value => setTrackedBody(value)} />
              </Section>
            </Section>
          </Flex.Item>
        </Flex>
      </Window.Content>
    </Window>
  );
};

const OrbitalMapDisplay = (props, context) => {
  const {
    zoomScale,
    setZoomScale,
    setTrackedBody,
    isTracking = false,
    dynamicXOffset,
    dynamicYOffset,
  } = props;

  const [
    offset,
    setOffset,
  ] = useLocalState(context, 'offset', [0, 0]);

  let lockedZoomScale = Math.max(Math.min(zoomScale, 4), 0.125);

  const { act, data } = useBackend(context);

  const {
    map_objects = [],
    update_index = 0,
  } = data;

  return (
    <>
      <Button
        position="absolute"
        icon="search-plus"
        right="20px"
        top="15px"
        fontSize="18px"
        color="grey"
        onClick={() => setZoomScale(zoomScale * 2)} />
      <Button
        position="absolute"
        icon="search-minus"
        right="20px"
        top="47px"
        fontSize="18px"
        color="grey"
        onClick={() => setZoomScale(zoomScale / 2)} />
      <DraggableClickableControl
        position="absolute"
        value={isTracking ? dynamicXOffset : offset[0]}
        dragMatrix={[-1, 0]}
        step={1}
        stepPixelSize={2 * zoomScale}
        onDrag={(e, value) => {
          if (!isTracking) {
            setOffset([value, offset[1]]);
          }
          setTrackedBody("None");
        }}
        onClick={(e, value) => {}}
        updateRate={5}>
        {control => (
          <DraggableClickableControl
            position="absolute"
            value={isTracking ? dynamicYOffset : offset[1]}
            dragMatrix={[0, -1]}
            step={1}
            stepPixelSize={2 * zoomScale}
            onDrag={(e, value) => {
              if (!isTracking) {
                setOffset([offset[0], value]);
              }
              setTrackedBody("None");
            }}
            onClick={(e, value) => {}}
            updateRate={5}>
            {control1 => (
              <>
                {control.inputElement}
                {control1.inputElement}
                <svg
                  onMouseDown={e => {
                    control.handleDragStart(e);
                    control1.handleDragStart(e);
                  }}
                  viewBox="-250 -250 500 500"
                  position="absolute"
                  overflowY="hidden">
                  <defs>
                    <pattern id="grid" width={100 * lockedZoomScale}
                      height={100 * lockedZoomScale}
                      patternUnits="userSpaceOnUse"
                      x={-(isTracking ? dynamicXOffset : offset[0]) * zoomScale}
                      y={-(isTracking ? dynamicYOffset : offset[1]) * zoomScale}>
                      <rect width={100 * lockedZoomScale}
                        height={100 * lockedZoomScale}
                        fill="url(#smallgrid)" />
                      <path
                        fill="none" stroke="#00FFFF" strokeWidth="1"
                        d={"M " + (100 * lockedZoomScale)+ " 0 L 0 0 0 " + (100 * lockedZoomScale)} />
                    </pattern>
                    <pattern id="smallgrid"
                      width={50 * lockedZoomScale}
                      height={50 * lockedZoomScale}
                      patternUnits="userSpaceOnUse">
                      <rect
                        width={50 * lockedZoomScale}
                        height={50 * lockedZoomScale}
                        fill="#1a1a1a" />
                      <path
                        fill="none"
                        stroke="#00FFFF"
                        strokeWidth="0.5"
                        d={"M " + (50 * lockedZoomScale) + " 0 L 0 0 0 "
                        + (50 * lockedZoomScale)} />
                    </pattern>
                  </defs>
                  <rect x="-50%" y="-50%" width="100%" height="100%"
                    fill="url(#grid)" />
                  {map_objects.map(map_object => (
                    <g key={map_object.id}>
                      <circle
                        cx={(map_object.position_x - (isTracking ? dynamicXOffset : offset[0])) * zoomScale}
                        cy={(map_object.position_y - (isTracking ? dynamicYOffset : offset[1])) * zoomScale}
                        r={Math.max(map_object.radius * zoomScale, 2)}
                        fill={map_object.render_mode === 'planet' ? '#fca635' : 
                              map_object.render_mode === 'beacon' ? '#f58473' :
                              map_object.render_mode === 'shuttle' ? '#a4eea4' : '#ffffff'}
                        stroke="#ffffff"
                        strokeWidth="1" />
                      <text
                        x={(map_object.position_x - (isTracking ? dynamicXOffset : offset[0]) + map_object.radius + 5) * zoomScale}
                        y={(map_object.position_y - (isTracking ? dynamicYOffset : offset[1])) * zoomScale}
                        fill="white"
                        fontSize={Math.min(12 * lockedZoomScale, 12)}>
                        {map_object.name}
                      </text>
                      {map_object.velocity_x !== 0 || map_object.velocity_y !== 0 ? (
                        <line
                          x1={(map_object.position_x - (isTracking ? dynamicXOffset : offset[0])) * zoomScale}
                          y1={(map_object.position_y - (isTracking ? dynamicYOffset : offset[1])) * zoomScale}
                          x2={(map_object.position_x + map_object.velocity_x * 10 - (isTracking ? dynamicXOffset : offset[0])) * zoomScale}
                          y2={(map_object.position_y + map_object.velocity_y * 10 - (isTracking ? dynamicYOffset : offset[1])) * zoomScale}
                          stroke="#00ff00"
                          strokeWidth="1" />
                      ) : null}
                    </g>
                  ))}
                </svg>
              </>
            )}
          </DraggableClickableControl>
        )}
      </DraggableClickableControl>
    </>
  );
};