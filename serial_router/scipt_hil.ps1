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

    public static void MoveMouse(int x, int y)
    {
        mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, (uint)x, (uint)y, 0, 0);
    }

    public static void PressNumLock()
    {
        keybd_event(VK_NUMLOCK, 0, KEYEVENTF_KEYDOWN, 0);
        keybd_event(VK_NUMLOCK, 0, KEYEVENTF_KEYUP, 0);
    }
}
"@

# Generate random coordinates
$random = [System.Random]::new()
$screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
$screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height
$randomX = $random.Next(0, $screenWidth)
$randomY = $random.Next(0, $screenHeight)

# Move the mouse to random coordinates
[MouseKeyboard]::MoveMouse($randomX, $randomY)

# Press the Num Lock key
[MouseKeyboard]::PressNumLock()
