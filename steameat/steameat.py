import ctypes
import sys
import platform
import datetime
import pathlib
import typing


def _get_library_path():
    dir = pathlib.Path(__file__).parent.resolve()
    is_64bits = sys.maxsize > (2**32)
    plat_system = platform.system().lower()
    if plat_system == 'windows':
        if is_64bits:
            lib_path = dir / 'lib' / 'win64' / 'sdkencryptedappticket64.dll'
        else:
            lib_path = dir / 'lib' / 'win32' / 'sdkencryptedappticket64.dll'
    elif plat_system == 'linux':
        if is_64bits:
            lib_path = dir / 'lib' / 'linux64' / 'libsdkencryptedappticket.so'
        else:
            lib_path = dir / 'lib' / 'linux32' / 'libsdkencryptedappticket.so'
    elif plat_system == 'darwin':
        # macOS has universal dylibs so no need for the 64bit check
        lib_path = dir / 'lib' / 'osx' / 'libsdkencryptedappticket.dylib'
    else:
        raise RuntimeError('Unsupported OS for SDKEncryptedAppTicket!')
    return str(lib_path.resolve())


def _load_steamencryptedappticket_library(library_path: str):
    lib = ctypes.cdll.LoadLibrary(library_path)
    # AppId is uint32_t
    # RTime32 is uint32
    # CSteamID is a class which has a uint64 as it's only member

    # k_nSteamEncryptedAppTicketSymmetricKeyLen = 32
    lib.SteamEncryptedAppTicket_BDecryptTicket.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint8), # ctypes.c_uint8 * k_nSteamEncryptedAppTicketSymmetricKeyLen,
        ctypes.c_int32
    )
    lib.SteamEncryptedAppTicket_BDecryptTicket.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_BIsTicketForApp.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.c_uint32 # AppId_t
    )
    lib.SteamEncryptedAppTicket_BIsTicketForApp.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_GetTicketIssueTime.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_GetTicketIssueTime.restype = ctypes.c_uint32 # RTime32

    lib.SteamEncryptedAppTicket_GetTicketSteamID.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint64) # CSteamID
    )
    lib.SteamEncryptedAppTicket_GetTicketSteamID.restype = None

    lib.SteamEncryptedAppTicket_GetTicketAppID.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_GetTicketAppID.restype = ctypes.c_uint32 # AppId_t

    lib.SteamEncryptedAppTicket_BUserOwnsAppInTicket.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.c_uint32 # AppId_t
    )
    lib.SteamEncryptedAppTicket_BUserOwnsAppInTicket.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_BUserIsVacBanned.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_BUserIsVacBanned.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_BGetAppDefinedValue.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32)
    )
    lib.SteamEncryptedAppTicket_BGetAppDefinedValue.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_GetUserVariableData.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32)
    )
    lib.SteamEncryptedAppTicket_GetUserVariableData.restype = ctypes.POINTER(ctypes.c_uint8)

    lib.SteamEncryptedAppTicket_BIsTicketSigned.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_BIsTicketSigned.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_BIsLicenseBorrowed.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_BIsLicenseBorrowed.restype = ctypes.c_bool

    lib.SteamEncryptedAppTicket_BIsLicenseTemporary.argtypes = (
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint32
    )
    lib.SteamEncryptedAppTicket_BIsLicenseTemporary.restype = ctypes.c_bool
    return lib


class ticket_data(object):


    def __init__(self, libthing, tk: bytes) -> None:
        self.issue_time = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.UTC)
        self.steam_id = 0
        self.app_id = 0
        self.is_vac_banned = False
        self.is_license_borrowed = False
        self.is_license_temporary = False
        self.user_data = bytes()
        self.app_defined_value = 0
        self.__ticket__ = tk
        tklen = len(self.__ticket__)
        self.__ticket_raw__ = (ctypes.c_uint8 * tklen).from_buffer_copy(self.__ticket__)
        self.__ticket_raw_length__ = ctypes.c_uint32(tklen)
        self.__lib__ = libthing


    def get_decrypted_ticket_bytes(self) -> bytes:
        return self.__ticket__


    def is_ticket_for_app(self, app_id: int) -> bool:
        return self.__lib__.SteamEncryptedAppTicket_BIsTicketForApp(
            self.__ticket_raw__,
            self.__ticket_raw_length__,
            ctypes.c_uint32(app_id)
        )


    def user_owns_app_in_ticket(self, app_id: int) -> bool:
        return self.__lib__.SteamEncryptedAppTicket_BUserOwnsAppInTicket(
            self.__ticket_raw__,
            self.__ticket_raw_length__,
            ctypes.c_uint32(app_id)
        )
    

    def is_ticket_signed(self, rsa_key: bytes) -> bool:
        rsakeylen = len(rsa_key)
        pubRSAKey = (ctypes.c_uint8 * rsakeylen).from_buffer_copy(rsa_key)
        return self.__lib__.SteamEncryptedAppTicket_BIsTicketSigned(
            self.__ticket_raw__,
            self.__ticket_raw_length__,
            pubRSAKey,
            ctypes.c_uint32(rsakeylen)
        )


class library_context(object):
    def __init__(self, library_path: typing.Union[str, None] = None):
        if library_path:
            self.__libpath__ = library_path
        else:
            self.__libpath__ = _get_library_path()
        self.__lib__ = _load_steamencryptedappticket_library(self.__libpath__)


    def get_library_path(self):
        return self.__libpath__


    def decrypt(self, ticket: bytes, key: bytes):
        ticketlen = len(ticket)
        keylen = len(key)

        rgubTicketEncrypted = (ctypes.c_uint8 * ticketlen).from_buffer_copy(ticket)
        cubTicketEncrypted = ctypes.c_uint32(ticketlen)
        rgubKey = (ctypes.c_uint8 * keylen).from_buffer_copy(key)
        cubKey = ctypes.c_int32(keylen)

        decryptedTicket = bytearray(0x10000)
        ticketDecryptedLen = ctypes.c_uint32(len(decryptedTicket))
        rgubTicketDecrypted = (ctypes.c_uint8 * len(decryptedTicket)).from_buffer(decryptedTicket)
        pcubTicketDecrypted = ctypes.pointer(ticketDecryptedLen)

        result = self.__lib__.SteamEncryptedAppTicket_BDecryptTicket(
            rgubTicketEncrypted,
            cubTicketEncrypted,
            rgubTicketDecrypted,
            pcubTicketDecrypted,
            rgubKey,
            cubKey
        )

        if not result:
            # Failed!
            return None
        
        issueTime = self.__lib__.SteamEncryptedAppTicket_GetTicketIssueTime(
            rgubTicketDecrypted,
            ticketDecryptedLen
        )

        steamID = ctypes.c_uint64(0)
        psteamID = ctypes.pointer(steamID)
        self.__lib__.SteamEncryptedAppTicket_GetTicketSteamID(
            rgubTicketDecrypted,
            ticketDecryptedLen,
            psteamID
        )

        appID = self.__lib__.SteamEncryptedAppTicket_GetTicketAppID(
            rgubTicketDecrypted,
            ticketDecryptedLen
        )

        isVacBanned = self.__lib__.SteamEncryptedAppTicket_BUserIsVacBanned(
            rgubTicketDecrypted,
            ticketDecryptedLen
        )

        isLicenseBorrowed = self.__lib__.SteamEncryptedAppTicket_BIsLicenseBorrowed(
            rgubTicketDecrypted,
            ticketDecryptedLen
        )

        isLicenseTemporary = self.__lib__.SteamEncryptedAppTicket_BIsLicenseTemporary(
            rgubTicketDecrypted,
            ticketDecryptedLen
        )

        appDefinedValue = ctypes.c_uint32(0)
        pValue = ctypes.pointer(appDefinedValue)
        self.__lib__.SteamEncryptedAppTicket_BGetAppDefinedValue(
            rgubTicketDecrypted,
            ticketDecryptedLen,
            pValue
        )

        cubUserData = ctypes.c_uint32(0)
        pcubUserData = ctypes.pointer(cubUserData)
        userDataPointer = self.__lib__.SteamEncryptedAppTicket_GetUserVariableData(
            rgubTicketDecrypted,
            ticketDecryptedLen,
            pcubUserData
        )

        userData = bytes()
        try:
            userDataArrC = ctypes.cast(userDataPointer, ctypes.POINTER(ctypes.c_uint8 * cubUserData.value))
            userData = bytes(userDataArrC.contents)
        except:
            pass

        cutticket = bytes(decryptedTicket[:ticketDecryptedLen.value])
        tkdata = ticket_data(self.__lib__, cutticket)
        tkdata.app_id = appID
        tkdata.steam_id = steamID.value
        tkdata.is_vac_banned = isVacBanned
        tkdata.is_license_borrowed = isLicenseBorrowed
        tkdata.is_license_temporary = isLicenseTemporary
        tkdata.issue_time = datetime.datetime.utcfromtimestamp(
            issueTime
        )
        tkdata.user_data = userData
        tkdata.app_defined_value = appDefinedValue.value

        return tkdata


__all__ = [ 'library_context', 'ticket_data' ]        
