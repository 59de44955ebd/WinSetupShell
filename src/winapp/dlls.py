__dlls__ = ['advapi32', 'comctl32', 'comdlg32', 'gdi32', 'kernel32', 'shell32', 'user32', 'uxtheme']

from ctypes.wintypes import *
from .types import *

advapi32 = ctypes.windll.advapi32
#atl = ctypes.windll.atl
comctl32 = ctypes.windll.comctl32
comdlg32 = ctypes.windll.comdlg32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
#ole32 = ctypes.windll.Ole32
shell32 = ctypes.windll.shell32
#shlwapi = ctypes.windll.Shlwapi
user32 = ctypes.windll.user32
uxtheme = ctypes.windll.uxtheme

########################################
# advapi32
########################################
advapi32.RegCloseKey.argtypes = (HKEY,)
advapi32.RegCloseKey.restype = LSTATUS
advapi32.RegCreateKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegCreateKeyW.restype = LSTATUS
advapi32.RegOpenKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegOpenKeyW.restype = LSTATUS
advapi32.RegQueryValueExW.argtypes = (HKEY, LPCWSTR, LPDWORD, LPDWORD, LPVOID, LPDWORD)
advapi32.RegQueryValueExW.restype = LSTATUS
# POINTER(BYTE)
advapi32.RegSetValueExW.argtypes = (HKEY, LPCWSTR, DWORD, DWORD, LPVOID, DWORD)
advapi32.RegSetValueExW.restype = LSTATUS

########################################
# comctl32
########################################
comctl32.DefSubclassProc.argtypes = (HWND, UINT, WPARAM, LPARAM)
comctl32.DefSubclassProc.restype = LPARAM
# HIMAGELIST
comctl32.ImageList_Add.argtypes = (HANDLE, HBITMAP, HBITMAP)
#comctl32.ImageList_AddIcon.argtypes = (HANDLE, HANDLE)
comctl32.ImageList_AddIcon = lambda handle, hicon: comctl32.ImageList_ReplaceIcon(handle, -1, hicon)
comctl32.ImageList_BeginDrag.argtypes = (HANDLE, INT, INT, INT)
comctl32.ImageList_Create.restype = HANDLE
comctl32.ImageList_Destroy.argtypes = (HANDLE,)
#comctl32.ImageList_Destroy.argtypes = (HANDLE,)
# HIMAGELIST
comctl32.ImageList_Draw.argtypes = (HANDLE, INT, HDC, INT, INT, UINT)
comctl32.ImageList_GetIcon.argtypes = (HANDLE, INT, UINT)
comctl32.ImageList_GetIcon.restype = HICON
# HIMAGELIST
comctl32.ImageList_GetIconSize.argtypes = (HANDLE, LPINT, LPINT)
comctl32.ImageList_GetImageCount.argtypes = (HANDLE,)
# POINTER(IMAGEINFO)]
comctl32.ImageList_GetImageInfo.argtypes = (HANDLE, INT, LPVOID)
comctl32.ImageList_LoadImageW.argtypes = (HINSTANCE, LPCWSTR, INT, INT, COLORREF, UINT, UINT)
comctl32.ImageList_LoadImageW.restype = HANDLE
comctl32.ImageList_Merge.argtypes = (HANDLE, INT, HANDLE, INT, INT, INT)
comctl32.ImageList_Merge.restype = HANDLE
comctl32.ImageList_Remove.argtypes = (HANDLE, INT)
comctl32.ImageList_Replace.argtypes = (HANDLE, INT, HANDLE, HANDLE)
comctl32.ImageList_ReplaceIcon.argtypes = (HANDLE, INT, HICON)
#comctl32.SetWindowSubclass.argtypes = (HWND, SUBCLASSPROC, UINT_PTR, DWORD_PTR)

########################################
# comdlg32
########################################
comdlg32.GetOpenFileNameW.argtypes = (LPVOID,)
comdlg32.GetSaveFileNameW.argtypes = (LPVOID,)

########################################
# gdi32
########################################
gdi32.AddFontResourceW.argtypes = (LPCWSTR,)
gdi32.BitBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD)
gdi32.CreateBitmap.argtypes = (INT, INT, UINT, UINT, LPVOID)
gdi32.CreateBitmap.restype = HBITMAP
gdi32.CreateBitmapIndirect.restype = HBITMAP
gdi32.CreateCompatibleBitmap.argtypes = (HDC, INT, INT)
gdi32.CreateCompatibleBitmap.restype = HBITMAP
gdi32.CreateCompatibleDC.argtypes = (HDC,)
gdi32.CreateCompatibleDC.restype = HDC
gdi32.CreateDIBitmap.argtypes = (HDC, LPVOID, DWORD, LPVOID, LPVOID, UINT)
gdi32.CreateDIBitmap.restype = HDC
gdi32.CreateDIBSection.argtypes = (HDC, LPVOID, UINT, LPVOID, HANDLE, DWORD)
gdi32.CreateDIBSection.restype = HBITMAP
gdi32.CreateFontIndirectW.argtypes = (LPVOID,)  # LOGFONTW *lplf
gdi32.CreateFontIndirectW.restype = HFONT
gdi32.CreateFontW.argtypes = (INT, INT, INT, INT, INT, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, LPCWSTR)
gdi32.CreateFontW.restype = HFONT
gdi32.CreatePatternBrush.argtypes = (HBITMAP,)
gdi32.CreatePatternBrush.restype = HBRUSH
gdi32.CreateSolidBrush.argtypes = (COLORREF,)
gdi32.CreateSolidBrush.restype = HBRUSH
gdi32.DeleteDC.argtypes = (HDC,)
gdi32.DeleteObject.argtypes = (HANDLE,)
gdi32.DPtoLP.argtypes = (HDC, LPPOINT, INT)
gdi32.Ellipse.argtypes = (HDC, INT, INT, INT, INT)
#gdi32.EnumFontFamiliesExW.argtypes = (HDC, POINTER(LOGFONTW), FONTENUMPROCW, LPARAM, DWORD)
gdi32.EnumFontFamiliesExW.argtypes = (HDC, LPVOID, LPVOID, LPARAM, DWORD)
gdi32.ExtFloodFill.argtypes = (HDC, INT, INT, COLORREF, UINT)
gdi32.ExtTextOutW.argtypes = (HDC, INT, INT, UINT, LPRECT, LPCWSTR, UINT, LPINT)
gdi32.FillRgn.argtypes = (HDC, HRGN, HBRUSH)
gdi32.GetDeviceCaps.argtypes = (HDC, INT)
gdi32.GetDIBits.argtypes = (HDC, HBITMAP, UINT, UINT, LPVOID, LPVOID, UINT)
gdi32.GetDIBits.restype = INT
gdi32.GetObjectW.argtypes = (HDC, INT, LPVOID)
gdi32.GetPixel.argtypes = (HDC, INT, INT)
gdi32.GetStockObject.restype = HANDLE
gdi32.GetTextMetricsW.argtypes = (HDC, LPVOID)
gdi32.LineTo.argtypes = (HDC, INT, INT)
gdi32.MaskBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, HBITMAP, INT, INT, DWORD)
gdi32.MoveToEx.argtypes = (HDC, INT, INT, LPPOINT)
gdi32.Polygon.argtypes = (HDC, LPPOINT, INT)
gdi32.Rectangle.argtypes = (HDC, INT, INT, INT, INT)
gdi32.RoundRect.argtypes = (HDC, INT, INT, INT, INT, INT, INT)
gdi32.SelectObject.argtypes = (HDC, HANDLE)
gdi32.SelectObject.restype = HANDLE
gdi32.SetBkColor.argtypes = (HDC, COLORREF)
gdi32.SetBkMode.argtypes = (HDC, INT)
gdi32.SetDCBrushColor.argtypes = (HDC, COLORREF)
gdi32.SetDCPenColor.argtypes = (HDC, COLORREF)
gdi32.SetDIBits.argtypes = (HDC, HBITMAP, UINT, UINT, LPVOID, LPVOID, UINT)
gdi32.SetMapMode.argtypes = (HDC, INT)
gdi32.SetPixel.argtypes = (HDC, INT, INT, COLORREF)
gdi32.SetStretchBltMode.argtypes = (HDC, INT)
gdi32.SetTextColor.argtypes = (HDC, COLORREF)
gdi32.SetViewportExtEx.argtypes = (HDC, INT, INT, LPSIZE)
gdi32.SetWindowExtEx.argtypes = (HDC, INT, INT, LPSIZE)
gdi32.StretchBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, INT, INT, DWORD)
gdi32.SaveDC.argtypes = (HDC,)
gdi32.RestoreDC.argtypes = (HDC, INT)

########################################
# kernel32
########################################
kernel32.CloseHandle.argtypes = (HANDLE,)
# LPSECURITY_ATTRIBUTES
kernel32.CreateFileW.argtypes = (LPCWSTR, DWORD, DWORD, LPVOID, DWORD, DWORD, HANDLE)
kernel32.CreateFileW.restype = HANDLE
# POINTER(SECURITY_ATTRIBUTES)
kernel32.CreatePipe.argtypes = (LPHANDLE, LPHANDLE, LPVOID, DWORD)
#kernel32.CreateProcessW.argtypes = (LPCWSTR, LPWSTR, POINTER(SECURITY_ATTRIBUTES), POINTER(SECURITY_ATTRIBUTES), BOOL, DWORD, LPVOID, LPCWSTR, POINTER(STARTUPINFOW), POINTER(PROCESS_INFORMATION))
kernel32.CreateProcessW.argtypes = (LPCWSTR, LPWSTR, LPVOID, LPVOID, BOOL, DWORD, LPVOID, LPCWSTR, LPVOID, LPVOID)
kernel32.DuplicateHandle.argtypes = (HANDLE, HANDLE, HANDLE, LPHANDLE, DWORD, BOOL, DWORD)
#kernel32.EnumResourceNamesW.argtypes = (HMODULE, LPCWSTR, ENUMRESNAMEPROCW, LONG_PTR)
#kernel32.EnumResourceNamesW.restype = BOOL
kernel32.FindResourceW.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
kernel32.FindResourceW.restype = HANDLE
kernel32.FreeLibrary.argtypes = (HMODULE,)
kernel32.GetBinaryTypeW.argtypes = (LPCWSTR, LPDWORD)
kernel32.GetCurrentProcess.restype = HANDLE
kernel32.GetExitCodeProcess.argtypes = (HANDLE, LPDWORD)
kernel32.GetModuleHandleW.argtypes = (LPCWSTR,)
kernel32.GetModuleHandleW.restype = HMODULE
kernel32.GetProcAddress.argtypes = (HMODULE, LPCSTR)
#FARPROC
kernel32.GetProcAddress.restype = HANDLE
kernel32.GetProcessId.argytypes = (HANDLE,)
kernel32.GlobalAlloc.argtypes = (UINT, DWORD)
kernel32.GlobalAlloc.restype = HGLOBAL
kernel32.GlobalFree.argtypes =(HGLOBAL,)
kernel32.GlobalLock.argtypes = (HGLOBAL,)
kernel32.GlobalLock.restype = LPVOID
kernel32.GlobalSize.argtypes = (HGLOBAL,)
kernel32.GlobalUnlock.argtypes = (HANDLE,)
kernel32.K32GetProcessImageFileNameW.argtypes = (HANDLE, LPWSTR, DWORD)
kernel32.LCIDToLocaleName.argtypes = (INT, LPWSTR, INT, DWORD)
kernel32.LoadLibraryExW.argtypes = (LPCWSTR, HANDLE, DWORD)
kernel32.LoadLibraryExW.restype = HANDLE
kernel32.LoadLibraryW.restype = HANDLE
kernel32.LoadResource.argtypes = (HANDLE, HANDLE)
kernel32.LoadResource.restype = HANDLE
kernel32.LocalAlloc.argtypes = (UINT, ctypes.c_size_t)
kernel32.LocalAlloc.restype = HLOCAL
kernel32.LocalFree.argtypes = (HLOCAL,)
kernel32.LocalFree.restype = HLOCAL
kernel32.LocalLock.argtypes = (HGLOBAL,)
kernel32.LocalLock.restype = LPVOID
kernel32.LocalUnlock.argtypes = (HANDLE,)
kernel32.LockResource.argtypes = (HANDLE,)
kernel32.LockResource.restype = HANDLE
kernel32.OpenProcess.argtypes = (DWORD, BOOL, DWORD)
kernel32.OpenProcess.restype = HANDLE
kernel32.PeekNamedPipe.argtypes = (HANDLE, LPVOID, DWORD, LPDWORD, LPDWORD, LPDWORD)
kernel32.QueryFullProcessImageNameW.argtypes = (HANDLE, DWORD, LPWSTR, LPDWORD)
# POINTER(OVERLAPPED))
kernel32.ReadFile.argtypes = (HANDLE, LPVOID, DWORD, LPDWORD, LPVOID)
kernel32.SetFileAttributesW.argtypes = (LPCWSTR, DWORD)
kernel32.SetThreadExecutionState.argtypes = (UINT,)
kernel32.SetThreadExecutionState.restype = UINT
kernel32.SizeofResource.argtypes = (HANDLE, HANDLE)

########################################
# shell32
########################################
shell32.DragAcceptFiles.argtypes = (HWND, BOOL)
shell32.DragFinish.argtypes = (WPARAM,)
shell32.DragQueryFileW.argtypes = (WPARAM, UINT, LPWSTR, UINT)
shell32.DragQueryPoint.argtypes = (WPARAM, LPPOINT)
shell32.RunFileDlg = shell32[61]
shell32.RunFileDlg.argtypes = (HWND, HANDLE, LPWSTR, LPWSTR, LPWSTR, UINT)
shell32.ShellExecuteW.argtypes = (HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT)
shell32.ShellExecuteW.restype = HINSTANCE
shell32.Shell_NotifyIconW.argtypes = (DWORD, LPVOID)
shell32.SHChangeNotify.argtypes = (LONG, UINT, LPVOID, LPVOID)
# first arg LPVOID since both LPCWSTR and PIDL are allowed
shell32.SHGetFileInfoW.argtypes = (LPVOID, DWORD, LPVOID, UINT, UINT)
shell32.SHGetFileInfoW.restype = DWORD_PTR
# POINTER(SHSTOCKICONINFO)
shell32.SHGetStockIconInfo.argtypes = (UINT, UINT, LPVOID)
shell32.SHObjectProperties.argtypes = (HWND, DWORD, LPWSTR, LPWSTR)

########################################
# user32
########################################
user32.AdjustWindowRect.argtypes = (LPRECT, DWORD, BOOL)
user32.AppendMenuW.argtypes = (HWND, UINT, UINT_PTR, LPCWSTR)
user32.CallNextHookEx.argtypes = (HANDLE, INT, WPARAM, LPARAM)
user32.CallNextHookEx.restype = LPARAM
user32.CheckMenuItem.argtypes = (HMENU, UINT, UINT)
user32.CopyImage.argtypes = (HANDLE, UINT, INT, INT, UINT)
user32.CopyImage.restype = HANDLE
#POINTER(ACCEL)
user32.CreateAcceleratorTableW.argtypes = (LPVOID, INT)
user32.CreateAcceleratorTableW.restype = HACCEL
# LPCDLGTEMPLATEW
user32.CreateDialogIndirectParamW.argtypes = (HINSTANCE, LPVOID, HWND, WNDPROC, LPARAM)
user32.CreateDialogIndirectParamW.restype = HWND
user32.CreateDialogParamW.argtypes = (HINSTANCE, LPCWSTR, HWND, DLGPROC, LPARAM)
user32.CreateDialogParamW.restype = HWND
# PBYTE
user32.CreateIconFromResourceEx.argtypes = (LPVOID, DWORD, BOOL, DWORD, INT, INT, UINT)
user32.CreateIconFromResourceEx.restype = HICON
# POINTER(ICONINFO)
user32.CreateIconIndirect.argtypes = (HANDLE,)
user32.CreateWindowExW.argtypes = (DWORD, LPCWSTR, LPCWSTR, DWORD, INT, INT, INT, INT, HWND, HMENU, HINSTANCE, LPVOID)
user32.DefDlgProcW.argtypes = (HWND, UINT, WPARAM, LPARAM)
user32.DefWindowProcW.argtypes = (HWND, UINT, WPARAM, LPARAM)
user32.DeleteMenu.argtypes = (HMENU, UINT, UINT)
user32.DestroyAcceleratorTable.restype = HANDLE
user32.DestroyWindow.argtypes = (HWND,)
user32.DialogBoxParamW.argtypes = (HINSTANCE, LPCWSTR, HWND, DLGPROC, LPARAM)
user32.DialogBoxParamW.restype = INT_PTR
user32.DispatchMessageW.argtypes = (LPMSG,)
user32.DrawEdge.argtypes = (HDC, LPRECT, UINT, UINT)
user32.DrawFocusRect.argtypes = (HANDLE, LPRECT)
user32.DrawIconEx.argtypes = (HDC, INT, INT, HICON, INT, INT, UINT, HBRUSH, UINT)
user32.DrawTextW.argtypes = (HANDLE, LPCWSTR, INT, LPRECT, UINT)
user32.EnableWindow.argytpes = (HWND, BOOL)
user32.FillRect.argtypes = (HANDLE, LPRECT, HBRUSH)
user32.FindWindowExW.argtypes = (HWND, HWND, LPCWSTR, LPCWSTR)
user32.FindWindowExW.restype = HWND
user32.FindWindowW.argtypes = (LPCWSTR, LPCWSTR)
user32.FindWindowW.restype = HWND
user32.FrameRect.argtypes = (HDC, LPRECT, HBRUSH)
user32.GetAsyncKeyState.restype = SHORT
user32.GetCapture.restype = HWND
user32.GetCaretPos.argtypes = (LPPOINT,)
user32.GetClassNameW.argtypes = (HWND, LPWSTR, INT)
user32.GetClientRect.argtypes = (HWND, LPRECT)
user32.GetClipboardData.restype = HANDLE
user32.GetDC.argtypes = (HWND,)
user32.GetDC.restype = HDC
user32.GetDCEx.argtypes = (HWND, HRGN, DWORD)
user32.GetDCEx.restype = HDC
user32.GetDesktopWindow.restype = HANDLE
user32.GetForegroundWindow.restype = HANDLE
user32.GetIconInfo.argtypes = (HANDLE, LPVOID)
# PMENUBARINFO
user32.GetMenuBarInfo.argtypes = (HWND, LONG, LONG, LPVOID)
user32.GetMenuItemCount.argtypes = (HMENU,)
# LPMENUITEMINFOW
user32.GetMenuItemInfoW.argtypes = (HMENU, UINT, BOOL, LPVOID)
user32.GetMenuStringW.argtypes = (HMENU, UINT, LPWSTR, INT, UINT)
user32.GetMessageW.argtypes = (LPMSG,HWND,UINT,UINT)
user32.GetParent.argtypes = (HWND,)
user32.GetParent.restype = HWND
user32.GetWindow.argtypes = (HANDLE, UINT)
user32.GetWindowDC.argtypes = (HWND,)
user32.GetWindowDC.restype = HDC
if IS_64_BIT:
    user32.GetWindowLongPtrA.argtypes = (HWND, LONG_PTR)
    user32.GetWindowLongPtrA.restype = ULONG
    user32.GetWindowLongPtrW.argtypes = (HWND, LONG_PTR)
    user32.GetWindowLongPtrW.restype = WNDPROC
user32.GetWindowLongW.argtypes = (HWND, INT)
user32.GetWindowLongW.restype = LONG
user32.GetWindowRect.argtypes = (HWND, LPRECT)
user32.GetWindowTextW.argtypes = (HWND, LPWSTR, INT)
user32.GetWindowThreadProcessId.argtypes = (HWND, LPDWORD)
user32.IntersectRect.argtypes = (LPRECT, LPRECT, LPRECT)
user32.InvalidateRect.argtypes = (HWND, LPRECT, BOOL)
user32.InvertRect.argtypes = (HDC, LPRECT)
user32.IsDialogMessageW.argtypes = (HWND, LPMSG)
user32.IsDialogMessageW.restype = BOOL
user32.IsWindowEnabled.argtypes = (HWND,)
user32.IsWindowVisible.argtypes = (HWND,)
user32.IsZoomed.argtypes = (HWND,)
user32.LoadAcceleratorsW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadAcceleratorsW.restype = HACCEL
user32.LoadBitmapW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadBitmapW.restype = HBITMAP
# LPCWSTR
user32.LoadCursorW.argtypes = (HINSTANCE, LPVOID)
user32.LoadIconW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadIconW.restype = HICON
user32.LoadImageW.argtypes = (HINSTANCE, LPCWSTR, UINT, INT, INT, UINT)
user32.LoadImageW.restype = HANDLE
user32.LoadMenuW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadMenuW.restype = HMENU
user32.LoadStringW.argtypes = (HINSTANCE, UINT, LPWSTR, INT)
user32.MapDialogRect.argtypes = (HWND, LPRECT)
user32.MapWindowPoints.argtypes = (HWND, HWND, LPVOID, UINT)
user32.MB_GetString.restype = LPCWSTR
user32.MessageBoxW.argtypes = (HWND, LPCWSTR, LPCWSTR, UINT)
user32.OffsetRect.argtypes = (LPRECT, INT, INT)
user32.OpenClipboard.argtypes = (HWND,)
user32.OpenClipboard.restype = BOOL
user32.PostMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.PostMessageW.restype = LONG_PTR
user32.PostThreadMessageW.argtypes = (DWORD, UINT, WPARAM, LPARAM)
user32.PrintWindow.argtypes = (HWND, HDC, UINT)
#POINTER(HICON)
user32.PrivateExtractIconsW.argtypes = (LPCWSTR, INT, INT, INT, LPVOID, LPUINT, UINT, UINT)
user32.RegisterHotKey.argtypes = (HWND, INT, UINT, UINT)
user32.RegisterShellHookWindow.argtypes = (HWND,)

user32.RegisterWindowMessageW.argtypes = (LPCWSTR,)
user32.RegisterWindowMessageW.restype = UINT

user32.ReleaseDC.argtypes = (HWND, HANDLE)
user32.SendDlgItemMessageW.argtypes = (HWND, INT, UINT, LPVOID, LPVOID)
# LPVOID to allow to send pointers
user32.SendMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.SendMessageW.restype = LONG_PTR
user32.SetCapture.argtypes = (HWND,)
user32.SetClassLongW.argtypes = (HWND, INT, LONG)
if IS_64_BIT:
    user32.SetClassLongPtrW.argtypes = (HWND, INT, LONG_PTR)
user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.restype = HANDLE
user32.SetClipboardData.restype = HANDLE
user32.SetLayeredWindowAttributes.argtypes = (HWND, COLORREF, BYTE, DWORD)
user32.SetMenu.argtypes = (HWND, HMENU)
user32.SetParent.argtypes = (HWND, HWND)
user32.SetSysColors.argtypes = (INT, LPINT, LPCOLORREF)
if IS_64_BIT:
    user32.SetWindowLongPtrA.argtypes = (HWND, LONG_PTR, ULONG)
    user32.SetWindowLongPtrA.restype = LONG
    user32.SetWindowLongPtrW.argtypes = (HWND, LONG_PTR, WNDPROC)
    user32.SetWindowLongPtrW.restype = WNDPROC
user32.SetWindowPos.argtypes = (HWND, LONG_PTR, INT, INT, INT, INT, UINT)
# HOOKPROC
user32.SetWindowsHookExW.argtypes = (INT, LPVOID, HINSTANCE, DWORD)
# HHOOK
user32.SetWindowsHookExW.restype = HANDLE
user32.SetWinEventHook.restype = HANDLE
user32.SystemParametersInfoW.argtypes = (UINT, UINT, LPVOID, UINT)
user32.TrackPopupMenu.argtypes = (HANDLE, UINT, INT, INT, INT, HANDLE, LPVOID)
user32.TrackPopupMenuEx.argtypes = (HANDLE, UINT, INT, INT, HANDLE, LPVOID)
user32.TranslateAcceleratorW.argtypes = (HWND, HACCEL, LPMSG)
user32.TranslateMessage.argtypes = (LPMSG,)
#HHOOK hhk
user32.UnhookWindowsHookEx.argtypes = (LPVOID,)
# LRESULT
user32.UnhookWindowsHookEx.restype = LPARAM
user32.UnregisterHotKey.argtypes = (HWND, INT)
user32.WindowFromPoint.argtypes = (POINT,)
user32.WindowFromPoint.restype = HWND

########################################
# UxTheme
########################################
# using fnAllowDarkModeForWindow = bool (WINAPI*)(HWND hWnd, bool allow); // ordinal 133
uxtheme.AllowDarkModeForWindow = uxtheme[133]
uxtheme.AllowDarkModeForWindow.argtypes = (HWND, BOOL)
uxtheme.AllowDarkModeForWindow.restype = BOOL
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-drawthemebackground
# HTHEME, HDC
uxtheme.DrawThemeBackground.argtypes = (HANDLE, HDC, INT, INT, LPRECT, LPRECT)
uxtheme.FlushMenuThemes = uxtheme[136]
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-getthemepartsize
# HTHEME, THEMESIZE
uxtheme.GetThemePartSize.argtypes = (HANDLE, HDC, INT, INT, LPRECT, UINT, LPSIZE)
uxtheme.OpenThemeData.argtypes = (HWND, LPCWSTR)
uxtheme.OpenThemeData.restype = HANDLE
# SetPreferredAppMode = PreferredAppMode(WINAPI*)(PreferredAppMode appMode);
uxtheme.SetPreferredAppMode = uxtheme[135]
uxtheme.SetWindowTheme.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
uxtheme.ShouldAppsUseDarkMode = uxtheme[136]
uxtheme.ShouldSystemUseDarkMode = uxtheme[138]
