Add-Type @"
using System;
using System.Runtime.InteropServices;

public class MouseKeyboard
{
    [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);

    [DllImport("user32.dll", CharSet = CharSet.Auto, CallingConvention = CallingConvention.StdCall)]
    public static extern uint keybd_event(byte bVk, byte bScan, uint dwFlags, uint dwExtraInfo);

    public const int MOUSEEVENTF_MOVE = 0x0001;
    public const int MOUSEEVENTF_ABSOLUTE = 0x8000;
    public const int KEYEVENTF_KEYDOWN = 0x0000;
    public const int KEYEVENTF_KEYUP = 0x0002;
    public const byte VK_NUMLOCK = 0x90;
    public const byte VK_MENU = 0x12; // Alt key
    public const byte VK_TAB = 0x09; // Tab key

    public static void MoveMouse(int x, int y)
    {
        mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, (uint)x, (uint)y, 0, 0);
    }

    public static void PressNumLock()
    {
        keybd_event(VK_NUMLOCK, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(VK_NUMLOCK, 0, KEYEVENTF_KEYUP, 0);
    }

    public static void PressAltTab()
    {
        keybd_event(VK_MENU, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(VK_TAB, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0);
        keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0);
    }
}
"@

# Infinite loop
while ($true) {
    # Generate random coordinates
    $random = [System.Random]::new()
    $screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
    $screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height
    $randomX = $random.Next(0, $screenWidth)
    $randomY = $random.Next(0, $screenHeight)

    # Print the random coordinates
    Write-Host "Moving mouse to coordinates: X=$randomX, Y=$randomY"

    # Move the mouse to random coordinates
    [MouseKeyboard]::MoveMouse($randomX, $randomY)

    # Print the action of pressing Num Lock
    Write-Host "Pressing Num Lock key"

    # Press the Num Lock key
    [MouseKeyboard]::PressNumLock()

    # Print the action of pressing Alt+Tab
    Write-Host "Pressing Alt+Tab"

    # Press Alt+Tab
    [MouseKeyboard]::PressAltTab()

    # Generate a random wait time between 1 and 5 seconds
    $randomWaitTime = $random.Next(1, 6)
    Write-Host "Waiting for $randomWaitTime seconds"

    # Wait for the random time
    Start-Sleep -Seconds $randomWaitTime
}
