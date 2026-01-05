import os

from ctypes import *
from ctypes.wintypes import *

from winapp.const import *
from winapp.dlls import advapi32, kernel32

IS_CONSOLE = kernel32.GetStdHandle(STD_OUTPUT_HANDLE) != 0

class PROCESS_INFORMATION(Structure):
    _fields_ = [
        ('hProcess',            HANDLE),
        ('hThread',             HANDLE),
        ('dwProcessId',         DWORD),
        ('dwThreadId',          DWORD),
    ]

class SECURITY_ATTRIBUTES(Structure):
    def __init__(self, *args, **kwargs):
        super(SECURITY_ATTRIBUTES, self).__init__(*args, **kwargs)
        self.nLength = sizeof(self)
    _fields_ = [
        ('nLength',                 DWORD),
        ('lpSecurityDescriptor',    LPVOID),
        ('bInheritHandle',          BOOL),
    ]

class SHELLEXECUTEINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(SHELLEXECUTEINFOW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ('cbSize',          DWORD),
        ('fMask',           ULONG),
        ('hwnd',            HWND),
        ('lpVerb',          LPCWSTR),
        ('lpFile',          LPCWSTR),
        ('lpParameters',    LPCWSTR),
        ('lpDirectory',     LPCWSTR),
        ('nShow',           INT),
        ('hInstApp',        HINSTANCE),
        ('lpIDList',        LPVOID),
        ('lpClass',         LPCWSTR),
        ('hkeyClass',       HKEY),
        ('dwHotKey',        DWORD),
        ('hIcon',           HANDLE),
        ('hProcess',        HANDLE)
    ]

class STARTUPINFOW(Structure):
    def __init__(self, *args, **kwargs):
        super(STARTUPINFOW, self).__init__(*args, **kwargs)
        self.cb = sizeof(self)
    _fields_ = [
        ('cb',                    DWORD ),
        ('lpReserved',            LPWSTR),
        ('lpDesktop',             LPWSTR),
        ('lpTitle',               LPWSTR),
        ('dwX',                   DWORD),
        ('dwY',                   DWORD),
        ('dwXSize',               DWORD),
        ('dwYSize',               DWORD),
        ('dwXCountChars',         DWORD),
        ('dwYCountChars',         DWORD),
        ('dwFillAttribute',       DWORD),
        ('dwFlags',               DWORD),
        ('wShowWindow',           WORD),
        ('cbReserved2',           WORD),
        ('lpReserved2',           LPBYTE),
        ('hStdInput',             HANDLE),
        ('hStdOutput',            HANDLE),
        ('hStdError',             HANDLE),
    ]

########################################
#
########################################
def run_command(command_line: str, cwd: str = '') -> tuple[bytes, bytes, int]:

    h_child_stdout_read = HANDLE()
    h_child_stdout_write = HANDLE()
    h_child_stdout_read_dup = HANDLE()

    h_child_stderr_read = HANDLE()
    h_child_stderr_write = HANDLE()
    h_child_stderr_read_dup = HANDLE()

    sec_attr = SECURITY_ATTRIBUTES()
    sec_attr.bInheritHandle = 1

    # Create a pipe for the child process's STDOUT.
    if not kernel32.CreatePipe(byref(h_child_stdout_read), byref(h_child_stdout_write), byref(sec_attr), 0):
        raise Exception(f'CreatePipe failed with error {kernel32.GetLastError()}')

    # Create a pipe for the child process's STDERR.
    if not kernel32.CreatePipe(byref(h_child_stderr_read), byref(h_child_stderr_write), byref(sec_attr), 0):
        raise Exception(f'CreatePipe failed with error {kernel32.GetLastError()}')

    h_proc = kernel32.GetCurrentProcess()

    # Create noninheritable read handle and close the inheritable read handle.
    ok = kernel32.DuplicateHandle(
        h_proc,
        h_child_stdout_read,
        h_proc,
        byref(h_child_stdout_read_dup),
        0,
        0,
        DUPLICATE_SAME_ACCESS
    )

    kernel32.CloseHandle(h_child_stdout_read)

    if not ok:
        kernel32.CloseHandle(h_child_stderr_read)
        raise Exception(f'DuplicateHandle failed for STDOUT with error {kernel32.GetLastError()}')

    # Create noninheritable read handle and close the inheritable read handle.
    ok = kernel32.DuplicateHandle(
        h_proc,
        h_child_stderr_read,
        h_proc,
        byref(h_child_stderr_read_dup),
        0,
        0,
        DUPLICATE_SAME_ACCESS
    )

    kernel32.CloseHandle(h_child_stderr_read)

    if not ok:
        raise Exception(f'DuplicateHandle failed for STDERR with error {kernel32.GetLastError()}')

    startup_info = STARTUPINFOW()
    startup_info.hStdError = h_child_stderr_write
    startup_info.hStdOutput = h_child_stdout_write
    startup_info.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW

    proc_info = PROCESS_INFORMATION()

    ok = kernel32.CreateProcessW(
        None,
        command_line,
        None,               # process security attributes
        None,               # primary thread security attributes
        1,                  # handles are inherited
        0,                  # dwCreationFlags
        None,               # use parent's environment
        cwd if cwd else None,
        byref(startup_info),
        byref(proc_info)
    )

    if not ok:
        raise Exception(f'CreateProcess failed with error {kernel32.GetLastError()}')

    kernel32.CloseHandle(proc_info.hThread)

    # Close the write end of the pipe before reading from the read end of the pipe.
    if not kernel32.CloseHandle(h_child_stdout_write):
        kernel32.CloseHandle(proc_info.hProcess)
        raise Exception(f'CloseHandle failed for STDOUT with error {kernel32.GetLastError()}')
    if not kernel32.CloseHandle(h_child_stderr_write):
        kernel32.CloseHandle(proc_info.hProcess)
        raise Exception(f'CloseHandle failed for STDERR with error {kernel32.GetLastError()}')

    bytes_available = DWORD()
    res_stdout = bytearray()
    res_stderr = bytearray()

    while True:

        # stdout
        ok = kernel32.PeekNamedPipe(h_child_stdout_read_dup, None, 0, None, byref(bytes_available), None)
        if not ok:
            break
        if bytes_available.value:
            buf = create_string_buffer(bytes_available.value)
            kernel32.ReadFile(h_child_stdout_read_dup, buf, bytes_available, None, None)
            res_stdout += buf.value

        # stderr
        ok = kernel32.PeekNamedPipe(h_child_stderr_read_dup, None, 0, None, byref(bytes_available), None)
        if not ok:
            break
        if bytes_available.value:
            buf = create_string_buffer(bytes_available.value)
            kernel32.ReadFile(h_child_stderr_read_dup, buf, bytes_available, None, None)
            res_stderr += buf.value

    exit_code = DWORD()
    kernel32.GetExitCodeProcess(proc_info.hProcess, byref(exit_code))
    kernel32.CloseHandle(proc_info.hProcess)

    return bytes(res_stdout), bytes(res_stderr), exit_code.value

########################################
#
########################################
def get_locales():
    hkey = HKEY()
    if advapi32.RegOpenKeyW(HKEY_USERS, '.DEFAULT\\Control Panel\\International' , byref(hkey)) != ERROR_SUCCESS:
        return None, None

    data = DWORD()
    cbData = DWORD()
    if advapi32.RegQueryValueExW(hkey, 'Locale', None, None, None, byref(cbData)) == ERROR_SUCCESS:
        data = create_unicode_buffer(cbData.value // sizeof(WCHAR))
        if advapi32.RegQueryValueExW(hkey, 'Locale', None, None, data, byref(cbData)) == ERROR_SUCCESS:
            lcid_system = '0x' + data.value[-4:]
    advapi32.RegCloseKey(hkey)

    if not lcid_system:
        return None, None

    command = os.path.expandvars(f'%windir%\\system32\\Wpeutil.exe ListKeyboardLayouts {lcid_system}')
    out, err, exit_code = run_command(command)
    if exit_code != 0:
        return None, None

    out = out.decode('oem')
    locales = {}
    buf = create_unicode_buffer(85)
    for line in out.split('\n'):
        if line.startswith('ID:'):
            lcid = eval('0x' + line.rstrip()[-8:])
            if lcid > 0xFFFF:
                continue
            res = kernel32.LCIDToLocaleName(lcid, buf, 85, 0)
            if res == 0:
                continue
            locales[lcid] = buf.value

    return eval(lcid_system), dict(sorted(locales.items(), key=lambda item: item[1]))
