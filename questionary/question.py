from __future__ import annotations

import sys
from typing import Any

import prompt_toolkit.patch_stdout
from prompt_toolkit import Application

from questionary import utils
from questionary.constants import DEFAULT_KBI_MESSAGE


def handle_kbi(
    kbi_msg: str | None = DEFAULT_KBI_MESSAGE,
    raise_on_kbi: bool = False,
    exit_on_kbi: bool = False,
) -> None:
    """Handle a KeyboardInterrupt received during a prompt. Called in all prompting methods in :class:`Question` when
    a KeyboardInterrupt is received

    Args:

        kbi_msg: The message to be printed on a keyboard interrupt (or None to not print a message).

        raise_on_kbi: Raise KeyboardInterrupt when one is received in a prompt if True

        exit_on_kbi: Exit the program when a KeyboardInterrupt is received in a prompt if True
    """
    if exit_on_kbi is True:
        exit(0)
    elif (not isinstance(exit_on_kbi, bool)) and isinstance(exit_on_kbi, int):
        exit(exit_on_kbi)
    elif raise_on_kbi:
        raise KeyboardInterrupt()
    else:
        if kbi_msg:
            print(f"\n{kbi_msg}\n")
        return None


class Question:
    """A question to be prompted.

    This is an internal class. Questions should be created using the
    predefined questions (e.g. text or password)."""

    application: "Application[Any]"
    should_skip_question: bool
    default: Any

    def __init__(self, application: "Application[Any]") -> None:
        self.application = application
        self.should_skip_question = False
        self.default = None

    async def ask_async(
        self,
        patch_stdout: bool = False,
        kbi_msg: str | None = DEFAULT_KBI_MESSAGE,
        raise_on_kbi: bool = False,
        exit_on_kbi: bool = False,
    ) -> Any:
        """Ask the question using asyncio and return user response.

        Args:
            patch_stdout: Ensure that the prompt renders correctly if other threads
                          are printing to stdout.

            kbi_msg: The message to be printed on a keyboard interrupt (or None to not print a message).

            raise_on_kbi: Raise KeyboardInterrupt when one is received in a prompt if True

            exit_on_kbi: Exit the program when a KeyboardInterrupt is received in a prompt if True

        Returns:
            `Any`: The answer from the question.
        """

        try:
            sys.stdout.flush()
            return await self.unsafe_ask_async(patch_stdout)
        except KeyboardInterrupt:
            return handle_kbi(
                kbi_msg=kbi_msg, exit_on_kbi=exit_on_kbi, raise_on_kbi=raise_on_kbi
            )

    def ask(
        self,
        patch_stdout: bool = False,
        kbi_msg: str | None = DEFAULT_KBI_MESSAGE,
        raise_on_kbi: bool = False,
        exit_on_kbi: bool = False,
    ) -> Any:
        """Ask the question synchronously and return user response.

        Args:
            patch_stdout: Ensure that the prompt renders correctly if other threads
                          are printing to stdout.

            kbi_msg: The message to be printed on a keyboard interrupt (or None to not print a message).

            raise_on_kbi: Raise KeyboardInterrupt when one is received in a prompt if True

            exit_on_kbi: Exit the program when a KeyboardInterrupt is received in a prompt if True

        Returns:
            `Any`: The answer from the question.
        """

        try:
            return self.unsafe_ask(patch_stdout)
        except KeyboardInterrupt:
            return handle_kbi(
                kbi_msg=kbi_msg, exit_on_kbi=exit_on_kbi, raise_on_kbi=raise_on_kbi
            )

    def unsafe_ask(self, patch_stdout: bool = False) -> Any:
        """Ask the question synchronously and return user response.

        Does not catch keyboard interrupts.

        Args:
            patch_stdout: Ensure that the prompt renders correctly if other threads
                          are printing to stdout.

        Returns:
            `Any`: The answer from the question.
        """

        if self.should_skip_question:
            return self.default

        if patch_stdout:
            with prompt_toolkit.patch_stdout.patch_stdout():
                return self.application.run()
        else:
            return self.application.run()

    def skip_if(self, condition: bool, default: Any = None) -> "Question":
        """Skip the question if flag is set and return the default instead.

        Args:
            condition: A conditional boolean value.
            default: The default value to return.

        Returns:
            :class:`Question`: `self`.
        """

        self.should_skip_question = condition
        self.default = default
        return self

    async def unsafe_ask_async(self, patch_stdout: bool = False) -> Any:
        """Ask the question using asyncio and return user response.

        Does not catch keyboard interrupts.

        Args:
            patch_stdout: Ensure that the prompt renders correctly if other threads
                          are printing to stdout.

        Returns:
            `Any`: The answer from the question.
        """

        if self.should_skip_question:
            return self.default

        if not utils.ACTIVATED_ASYNC_MODE:
            await utils.activate_prompt_toolkit_async_mode()

        if patch_stdout:
            with prompt_toolkit.patch_stdout.patch_stdout():
                r = self.application.run_async()
        else:
            r = self.application.run_async()

        if utils.is_prompt_toolkit_3():
            return await r
        else:
            return await r.to_asyncio_future()  # type: ignore[attr-defined]
