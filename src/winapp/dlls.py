from ctypes import windll, c_uint, POINTER, c_int, c_void_p, c_wchar_p, Structure, c_size_t
from ctypes.wintypes import *

from .wintypes_extended import WNDPROC, DLGPROC, LONG_PTR, ENUMRESNAMEPROCW, ACCEL, FONTENUMPROCW, LOGFONTW, DWORD_PTR,   SUBCLASSPROC, INT_PTR, UINT_PTR

advapi32 = windll.Advapi32
atl = windll.atl
comctl32 = windll.Comctl32
comdlg32 = windll.comdlg32
gdi32 = windll.Gdi32
kernel32 = windll.Kernel32
ole32 = windll.Ole32
shell32 = windll.shell32
shlwapi = windll.Shlwapi
user32 = windll.user32
uxtheme = windll.UxTheme

########################################
# advapi32
########################################
LSTATUS = LONG
PHKEY = POINTER(HKEY)

advapi32.RegCloseKey.argtypes = (HKEY, )
advapi32.RegCloseKey.restype = LSTATUS
advapi32.RegCreateKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegCreateKeyW.restype = LSTATUS
advapi32.RegOpenKeyW.argtypes = (HKEY, LPCWSTR, PHKEY)
advapi32.RegOpenKeyW.restype = LSTATUS
advapi32.RegQueryValueExW.argtypes = (HKEY, LPCWSTR, POINTER(DWORD), POINTER(DWORD), c_void_p, POINTER(DWORD))
advapi32.RegQueryValueExW.restype = LSTATUS
advapi32.RegSetValueExW.argtypes = (HKEY, LPCWSTR, DWORD, DWORD, c_void_p, DWORD)  # POINTER(BYTE)
advapi32.RegSetValueExW.restype = LSTATUS

########################################
# comctl32
########################################
comctl32.DefSubclassProc.argtypes = (HWND, UINT, WPARAM, LPARAM)
comctl32.DefSubclassProc.restype = LPARAM
comctl32.ImageList_Add.argtypes = (HANDLE, HBITMAP, HBITMAP)  # HIMAGELIST
comctl32.ImageList_AddIcon = lambda handle, hicon: comctl32.ImageList_ReplaceIcon(handle, -1, hicon)  #comctl32.ImageList_AddIcon.argtypes = (HANDLE, HANDLE)
comctl32.ImageList_BeginDrag.argtypes = (HANDLE, INT, INT, INT)
comctl32.ImageList_Create.restype = HANDLE
comctl32.ImageList_Destroy.argtypes = (HANDLE,)
comctl32.ImageList_Draw.argtypes = (HANDLE, INT, HDC, INT, INT, UINT)  # HIMAGELIST
comctl32.ImageList_GetIcon.argtypes = (HANDLE, INT, UINT)
comctl32.ImageList_GetIcon.restype = HICON
comctl32.ImageList_GetIconSize.argtypes = (HANDLE, POINTER(INT), POINTER(INT))  # HIMAGELIST
comctl32.ImageList_GetImageCount.argtypes = (HANDLE, )
comctl32.ImageList_GetImageInfo.argtypes = (HANDLE, INT, LPVOID)  # POINTER(IMAGEINFO)]
comctl32.ImageList_LoadImageW.argtypes = (HINSTANCE, LPCWSTR, INT, INT, COLORREF, UINT, UINT)
comctl32.ImageList_LoadImageW.restype = HANDLE
comctl32.ImageList_Merge.argtypes = (HANDLE, INT, HANDLE, INT, INT, INT)
comctl32.ImageList_Merge.restype = HANDLE
comctl32.ImageList_Remove.argtypes = (HANDLE, INT)
comctl32.ImageList_Replace.argtypes = (HANDLE, INT, HANDLE, HANDLE)
comctl32.ImageList_ReplaceIcon.argtypes = (HANDLE, INT, HICON)
comctl32.SetWindowSubclass.argtypes = (HWND, SUBCLASSPROC, UINT_PTR, DWORD_PTR)

########################################
# gdi32
########################################
gdi32.BitBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD)
gdi32.CreateBitmap.argtypes = (INT, INT, UINT, UINT, LPVOID)
gdi32.CreateBitmap.restype = HBITMAP
gdi32.CreateBitmapIndirect.restype = HBITMAP
gdi32.CreateCompatibleBitmap.argtypes = (HDC, INT, INT)
gdi32.CreateCompatibleBitmap.restype = HBITMAP
gdi32.CreateCompatibleDC.argtypes = (HDC, )
gdi32.CreateCompatibleDC.restype = HDC
gdi32.CreateDIBitmap.argtypes = (HDC, c_void_p, DWORD, LPVOID, c_void_p, UINT)
gdi32.CreateDIBitmap.restype = HDC
gdi32.CreateDIBSection.argtypes = (HDC, LPVOID, UINT, LPVOID, HANDLE, DWORD)
gdi32.CreateDIBSection.restype = HBITMAP
gdi32.CreateFontW.argtypes = (INT, INT, INT, INT, INT, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, LPCWSTR)
gdi32.CreateFontW.restype = HFONT
gdi32.CreatePatternBrush.argtypes = (HBITMAP, )
gdi32.CreatePatternBrush.restype = HBRUSH
gdi32.CreateSolidBrush.argtypes = (COLORREF, )
gdi32.CreateSolidBrush.restype = HBRUSH
gdi32.DeleteDC.argtypes = (HDC, )
gdi32.DeleteObject.argtypes = (HANDLE, )
gdi32.DPtoLP.argtypes = (HDC, POINTER(POINT), INT)
gdi32.Ellipse.argtypes = (HDC, INT, INT, INT, INT)
gdi32.EnumFontFamiliesExW.argtypes = (HDC, POINTER(LOGFONTW), FONTENUMPROCW, LPARAM, DWORD)
gdi32.ExtFloodFill.argtypes = (HDC, INT, INT, COLORREF, UINT)
gdi32.ExtTextOutW.argtypes = (HDC, INT, INT, UINT, POINTER(RECT), LPCWSTR, UINT, POINTER(INT))
gdi32.FillRgn.argtypes = (HDC, HRGN, HBRUSH)
gdi32.GetDeviceCaps.argtypes = (HDC, INT)
gdi32.GetDIBits.argtypes = (HDC, HBITMAP, UINT, UINT, LPVOID, c_void_p, UINT)
gdi32.GetDIBits.restype = c_int
gdi32.GetObjectW.argtypes = (HDC, INT, LPVOID)
gdi32.GetPixel.argtypes = (HDC, INT, INT)
gdi32.GetStockObject.restype = HANDLE
gdi32.GetTextMetricsW.argtypes = (HDC, LPVOID)
gdi32.LineTo.argtypes = (HDC, INT, INT)
gdi32.MaskBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, HBITMAP, INT, INT, DWORD)
gdi32.MoveToEx.argtypes = (HDC, INT, INT, POINTER(POINT))
gdi32.Polygon.argtypes = (HDC, POINTER(POINT), INT)
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
gdi32.SetViewportExtEx.argtypes = (HDC, INT, INT, POINTER(SIZE))
gdi32.SetWindowExtEx.argtypes = (HDC, INT, INT, POINTER(SIZE))
gdi32.StretchBlt.argtypes = (HDC, INT, INT, INT, INT, HDC, INT, INT, INT, INT, DWORD)

gdi32.SaveDC.argtypes = (HDC,)
gdi32.RestoreDC.argtypes = (HDC, INT)

########################################
# kernel32
########################################
kernel32.AttachConsole.argtypes = (DWORD,)
kernel32.CloseHandle.argtypes = (HANDLE,)
kernel32.CreatePipe.argtypes = (POINTER(HANDLE), POINTER(HANDLE), LPVOID, DWORD)  # POINTER(SECURITY_ATTRIBUTES)
kernel32.CreateProcessW.argtypes = (
    LPCWSTR, LPWSTR,
    LPVOID,  # POINTER(SECURITY_ATTRIBUTES),
    LPVOID,  #POINTER(SECURITY_ATTRIBUTES),
    BOOL, DWORD, LPVOID, LPCWSTR,
    LPVOID,  #POINTER(STARTUPINFOW),
    LPVOID,  #POINTER(PROCESS_INFORMATION)
)
kernel32.DuplicateHandle.argtypes = (HANDLE, HANDLE, HANDLE, POINTER(HANDLE), DWORD, BOOL, DWORD)
kernel32.EnumResourceNamesW.argtypes = (HMODULE, LPCWSTR, ENUMRESNAMEPROCW, LONG_PTR)
kernel32.EnumResourceNamesW.restype = BOOL
kernel32.FindResourceW.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
kernel32.FindResourceW.restype = HANDLE
kernel32.FreeLibrary.argtypes = (HMODULE,)
kernel32.GetCurrentProcess.restype = HANDLE
kernel32.GetExitCodeProcess.argtypes = (HANDLE, LPDWORD)
kernel32.GetModuleHandleW.argtypes = (LPCWSTR,)
kernel32.GetModuleHandleW.restype = HMODULE
kernel32.GetProcAddress.argtypes = (HMODULE, LPCSTR)
kernel32.GetProcAddress.restype = HANDLE  #FARPROC
kernel32.GetProcessId.argytypes = (HANDLE,)
kernel32.GetStdHandle.argtypes = (DWORD,)
kernel32.GetStdHandle.restype = INT_PTR
kernel32.GlobalAlloc.argtypes = (UINT, DWORD)
kernel32.GlobalAlloc.restype = HGLOBAL
kernel32.GlobalLock.argtypes = (HGLOBAL, )
kernel32.GlobalLock.restype = LPVOID
kernel32.GlobalSize.argtypes = (HGLOBAL, )
kernel32.GlobalUnlock.argtypes = (HANDLE,)
kernel32.LoadLibraryExW.argtypes = (LPCWSTR, HANDLE, DWORD)
kernel32.LoadLibraryExW.restype = HANDLE
kernel32.LoadLibraryW.restype = HANDLE
kernel32.LoadResource.argtypes = (HANDLE, HANDLE)
kernel32.LoadResource.restype = HANDLE
kernel32.LocalAlloc.argtypes = (UINT, c_size_t)
kernel32.LocalAlloc.restype = HLOCAL
kernel32.LocalFree.argtypes = (HLOCAL,)
kernel32.LocalFree.restype = HLOCAL
kernel32.LocalLock.argtypes = (HGLOBAL, )
kernel32.LocalLock.restype = LPVOID
kernel32.LocalUnlock.argtypes = (HANDLE,)
kernel32.LockResource.argtypes = (HANDLE, )
kernel32.LockResource.restype = HANDLE
kernel32.OpenProcess.argtypes = (DWORD, BOOL, DWORD)
kernel32.OpenProcess.restype = HANDLE
kernel32.PeekNamedPipe.argtypes = (HANDLE, LPVOID, DWORD, POINTER(DWORD), POINTER(DWORD), POINTER(DWORD))
kernel32.ReadFile. argtypes = (HANDLE, LPVOID, DWORD, POINTER(DWORD), LPVOID)  # POINTER(OVERLAPPED))
kernel32.SetThreadExecutionState.argtypes = (UINT,)
kernel32.SetThreadExecutionState.restype = UINT
kernel32.SizeofResource.argtypes = (HANDLE, HANDLE)
kernel32.TerminateProcess.argtypes = (HANDLE, UINT)

########################################
# shell32
########################################
shell32.DragAcceptFiles.argtypes = (HWND, BOOL)
shell32.DragFinish.argtypes = (WPARAM, )
shell32.DragQueryFileW.argtypes = (WPARAM, UINT, LPWSTR, UINT)
shell32.DragQueryPoint.argtypes = (WPARAM, LPPOINT)
shell32.RunFileDlg = shell32[61]
shell32.RunFileDlg.argtypes = (HWND, HANDLE, LPWSTR, LPWSTR, LPWSTR, UINT)
shell32.ShellExecuteW.argtypes = (HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT)
shell32.ShellExecuteW.restype = HINSTANCE
shell32.Shell_NotifyIconW.argtypes = (DWORD, LPVOID)
shell32.SHGetFileInfoW.argtypes = (LPVOID, DWORD, LPVOID, UINT, UINT)  # first arg LPVOID since both LPCWSTR and PIDL are allowed
shell32.SHGetFileInfoW.restype = DWORD_PTR  #POINTER(DWORD) #DWORD_PTR
shell32.SHGetStockIconInfo.argtypes = (UINT, UINT, LPVOID)  # POINTER(SHSTOCKICONINFO)
shell32.SHObjectProperties.argtypes = (HWND, DWORD, LPWSTR, LPWSTR)

########################################
# user32
########################################
user32.AdjustWindowRect.argtypes = (POINTER(RECT), DWORD, BOOL)
user32.AppendMenuW.argtypes = (HWND, UINT, UINT_PTR, LPCWSTR)
user32.CallNextHookEx.argtypes = (HANDLE, INT, WPARAM, LPARAM)
user32.CallNextHookEx.restype = LPARAM
user32.CheckMenuItem.argtypes = (HMENU, UINT, UINT)
user32.CopyImage.argtypes = (HANDLE, UINT, INT, INT, UINT)
user32.CopyImage.restype = HANDLE
user32.CreateAcceleratorTableW.argtypes = (POINTER(ACCEL), INT)
user32.CreateAcceleratorTableW.restype = HACCEL
user32.CreateDialogIndirectParamW.argtypes = (HINSTANCE, LPVOID, HWND, WNDPROC, LPARAM)  # LPCDLGTEMPLATEW
user32.CreateDialogIndirectParamW.restype = HWND
user32.CreateDialogParamW.argtypes = (HINSTANCE, LPCWSTR, HWND, DLGPROC, LPARAM)
user32.CreateDialogParamW.restype = HWND
user32.CreateIconFromResourceEx.argtypes = (c_void_p, DWORD, BOOL, DWORD, INT, INT, UINT)  # PBYTE
user32.CreateIconFromResourceEx.restype = HICON
user32.CreateIconIndirect.argtypes = (HANDLE, )  # POINTER(ICONINFO)
user32.CreatePopupMenu.restype = HMENU
user32.CreateWindowExW.argtypes = (DWORD, LPCWSTR, LPCWSTR, DWORD, INT, INT, INT, INT, HWND, HMENU, HINSTANCE, LPVOID)
user32.DefDlgProcW.argtypes = (HWND, c_uint, WPARAM, LPARAM)
user32.DefWindowProcW.argtypes = (HWND, c_uint, WPARAM, LPARAM)
user32.DeleteMenu.argtypes = (HMENU, UINT, UINT)
user32.DestroyAcceleratorTable.restype = HANDLE
user32.DestroyWindow.argtypes = (HWND,)
user32.DialogBoxParamW.argtypes = (HINSTANCE, LPCWSTR, HWND, DLGPROC, LPARAM)
user32.DialogBoxParamW.restype = INT_PTR
user32.DispatchMessageW.argtypes = (POINTER(MSG),)
user32.DrawEdge.argtypes = (HDC, POINTER(RECT), UINT, UINT)
user32.DrawFocusRect.argtypes = (HANDLE, POINTER(RECT))
user32.DrawIconEx.argtypes = (HDC, INT, INT, HICON, INT, INT, UINT, HBRUSH, UINT)
user32.DrawTextW.argtypes = (HANDLE, LPCWSTR, INT, POINTER(RECT), UINT)
user32.EnableWindow.argytpes = (HWND, BOOL)
user32.FillRect.argtypes = (HANDLE, POINTER(RECT), HBRUSH)
user32.FindWindowExW.argtypes = (HWND, HWND, LPCWSTR, LPCWSTR)
user32.FindWindowExW.restype = HWND
user32.FindWindowW.argtypes = (LPCWSTR, LPCWSTR)
user32.FindWindowW.restype = HWND
user32.FrameRect.argtypes = (HDC, POINTER(RECT), HBRUSH)
user32.GetCapture.restype = HWND
user32.GetCaretPos.argtypes = (POINTER(POINT),)
user32.GetClassNameW.argtypes = (HWND, LPWSTR, INT)
user32.GetClientRect.argtypes = (HWND, POINTER(RECT))
user32.GetClipboardData.restype = HANDLE
user32.GetDC.argtypes = (HWND,)
user32.GetDC.restype = HDC
user32.GetDCEx.argtypes = (HWND, HRGN, DWORD)
user32.GetDCEx.restype = HDC
user32.GetDesktopWindow.restype = HANDLE

user32.GetDpiForWindow.argtypes = (HWND,)
user32.GetDpiForWindow.restype = UINT

user32.GetForegroundWindow.restype = HANDLE
user32.GetIconInfo.argtypes = (HANDLE, LPVOID)
user32.GetMenuBarInfo.argtypes = (HWND, LONG, LONG, LPVOID)  # PMENUBARINFO
user32.GetMenuItemInfoW.argtypes = (HMENU, UINT, BOOL, LPVOID)  # LPMENUITEMINFOW
user32.GetMenuStringW.argtypes = (HMENU, UINT, LPWSTR, INT, UINT)
user32.GetMessageW.argtypes = (POINTER(MSG),HWND,UINT,UINT)
user32.GetParent.argtypes = (HWND,)
user32.GetParent.restype = HWND
user32.GetWindow.argtypes = (HANDLE, UINT)
user32.GetWindowDC.argtypes = (HWND,)
user32.GetWindowDC.restype = HDC
user32.GetWindowLongPtrA.argtypes = (HWND, LONG_PTR)
user32.GetWindowLongPtrA.restype = ULONG
user32.GetWindowLongPtrW.argtypes = (HWND, LONG_PTR)
user32.GetWindowLongPtrW.restype = WNDPROC
user32.GetWindowLongW.argtypes = (HWND, INT)
user32.GetWindowLongW.restype = LONG
user32.GetWindowRect.argtypes = (HWND, POINTER(RECT))
user32.GetWindowTextW.argtypes = (HWND, LPWSTR, INT)
user32.GetWindowThreadProcessId.argtypes = (HANDLE, POINTER(DWORD))
user32.IntersectRect.argtypes = (POINTER(RECT), POINTER(RECT), POINTER(RECT))
user32.InvalidateRect.argtypes = (HWND, POINTER(RECT), BOOL)
user32.InvertRect.argtypes = (HDC, POINTER(RECT))
user32.IsDialogMessageW.argtypes = (HWND, POINTER(MSG))
user32.IsDialogMessageW.restype = BOOL
user32.IsWindowEnabled.argtypes = (HWND, )
user32.IsWindowVisible.argtypes = (HWND, )
user32.IsZoomed.argtypes = (HWND, )
user32.LoadAcceleratorsW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadAcceleratorsW.restype = HACCEL
user32.LoadBitmapW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadBitmapW.restype = HBITMAP
user32.LoadCursorW.argtypes = (HINSTANCE, LPVOID)  # LPCWSTR
user32.LoadIconW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadIconW.restype = HICON
user32.LoadImageW.argtypes = (HINSTANCE, LPCWSTR, UINT, INT, INT, UINT)
user32.LoadImageW.restype = HANDLE
user32.LoadMenuW.argtypes = (HINSTANCE, LPCWSTR)
user32.LoadMenuW.restype = HMENU
user32.MapDialogRect.argtypes = (HWND, POINTER(RECT))
user32.MapWindowPoints.argtypes = (HWND, HWND, LPVOID, UINT)
user32.MB_GetString.restype = LPCWSTR
user32.MessageBoxW.argtypes = (HWND, LPCWSTR, LPCWSTR, UINT)
user32.OffsetRect.argtypes = (POINTER(RECT), INT, INT)
user32.OpenClipboard.argtypes = (HWND,)
user32.PostMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.PostMessageW.restype = LONG_PTR
user32.PostThreadMessageW.argtypes = (DWORD, UINT, WPARAM, LPARAM)
user32.PrintWindow.argtypes = (HWND, HDC, UINT)
user32.PrivateExtractIconsW.argtypes = (LPCWSTR, INT, INT, INT, POINTER(HICON), POINTER(UINT), UINT, UINT)
user32.RegisterShellHookWindow.argtypes = (HWND,)
user32.ReleaseDC.argtypes = (HWND, HANDLE)
user32.SendDlgItemMessageW.argtypes = (HWND, INT, UINT, LPVOID, LPVOID)
user32.SendMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)  # LPVOID to allow to send pointers
user32.SendMessageW.restype = LONG_PTR
user32.SetCapture.argtypes = (HWND,)
user32.SetClassLongPtrW.argtypes = (HWND, INT, LONG_PTR)
user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.argtypes = (UINT, HANDLE)
user32.SetClipboardData.restype = HANDLE
user32.SetClipboardData.restype = HANDLE
user32.SetLayeredWindowAttributes.argtypes = (HWND, COLORREF, BYTE, DWORD)
user32.SetMenu.argtypes = (HWND, HMENU)
user32.SetSysColors.argtypes = (INT, POINTER(INT), POINTER(COLORREF))
user32.SetWindowLongPtrA.argtypes = (HWND, LONG_PTR, ULONG)
user32.SetWindowLongPtrA.restype = LONG
user32.SetWindowLongPtrW.argtypes = (HWND, LONG_PTR, WNDPROC)
user32.SetWindowLongPtrW.restype = WNDPROC
user32.SetWindowPos.argtypes = (HWND, LONG_PTR, INT, INT, INT, INT, UINT)
user32.SetWindowsHookExW.argtypes = (INT, LPVOID, HINSTANCE, DWORD)  # HOOKPROC
user32.SetWindowsHookExW.restype = HANDLE  # HHOOK
user32.SetWinEventHook.restype = HANDLE
user32.TrackPopupMenu.argtypes = (HMENU, UINT, INT, INT, INT, HANDLE, c_void_p)
user32.TrackPopupMenuEx.argtypes = (HMENU, UINT, INT, INT, HANDLE, c_void_p)
user32.TranslateAcceleratorW.argtypes = (HWND, HACCEL, POINTER(MSG))
user32.TranslateMessage.argtypes = (POINTER(MSG),)
user32.UnhookWindowsHookEx.argtypes = (LPVOID,)  #HHOOK hhk
user32.UnhookWindowsHookEx.restype = LPARAM  # LRESULT

########################################
# UxTheme
########################################
# using fnAllowDarkModeForWindow = bool (WINAPI*)(HWND hWnd, bool allow); // ordinal 133
uxtheme.AllowDarkModeForWindow = uxtheme[133]
uxtheme.AllowDarkModeForWindow.argtypes = (HWND, BOOL)
uxtheme.AllowDarkModeForWindow.restype = BOOL
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-drawthemebackground
uxtheme.DrawThemeBackground.argtypes = (HANDLE, HDC, INT, INT, POINTER(RECT), POINTER(RECT))  # HTHEME, HDC
uxtheme.FlushMenuThemes = uxtheme[136]
# https://learn.microsoft.com/en-us/windows/win32/api/uxtheme/nf-uxtheme-getthemepartsize
uxtheme.GetThemePartSize.argtypes = (HANDLE, HDC, INT, INT, POINTER(RECT), UINT, POINTER(SIZE))  # HTHEME, THEMESIZE
uxtheme.OpenThemeData.argtypes = (HWND, LPCWSTR)
uxtheme.OpenThemeData.restype = HANDLE
# SetPreferredAppMode = PreferredAppMode(WINAPI*)(PreferredAppMode appMode);
uxtheme.SetPreferredAppMode = uxtheme[135]  # ordinal 135, in 1903
uxtheme.SetWindowTheme.argtypes = (HANDLE, LPCWSTR, LPCWSTR)
uxtheme.ShouldAppsUseDarkMode = uxtheme[136]
uxtheme.ShouldSystemUseDarkMode = uxtheme[138]
