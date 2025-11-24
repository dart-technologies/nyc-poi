import React from 'react';
import { DynamicColorIOS } from 'react-native';
import { NativeTabs, Icon, Label } from 'expo-router/unstable-native-tabs';

export default function TabLayout() {
  return (
    <NativeTabs
      // Styling for the tab bar
      labelStyle={{
        fontSize: 12,
        fontWeight: '600',
        color: DynamicColorIOS({
          dark: '#00d4ff',
          light: '#007aff',
        }),
      }}
      tintColor={DynamicColorIOS({
        dark: '#00d4ff',
        light: '#007aff',
      })}
    >
      {/* Discover Tab - First */}
      <NativeTabs.Trigger name="index">
        <Icon
          sf={{
            default: 'location',
            selected: 'location.fill'
          }}
          drawable="ic_discover"
        />
        <Label>Discover</Label>
      </NativeTabs.Trigger>

      {/* Chat Tab - Second */}
      <NativeTabs.Trigger name="two">
        <Icon
          sf={{
            default: 'message',
            selected: 'message.fill'
          }}
          drawable="ic_chat"
        />
        <Label>Chat</Label>
      </NativeTabs.Trigger>
    </NativeTabs>
  );
}
