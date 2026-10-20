"""Validate external-source identities and licenses recorded in ownership state."""
from __future__ import annotations

import re


GITHUB_URL = re.compile(
    r'^(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+)/'
    r'([A-Za-z0-9_.-]+?)(?:\.git)?$'
)


GIT_REF = re.compile(r'^[A-Za-z0-9._/-]+$')


LICENSE_SIGNATURES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    'MIT': ((
        'permission is hereby granted, free of charge, to any person obtaining a copy',
        'the above copyright notice and this permission notice shall be included',
        'the software is provided "as is", without warranty of any kind',
        'in no event shall the authors or copyright holders be liable',
    ), ()),
    'Apache-2.0': ((
        'apache license version 2.0, january 2004',
        'terms and conditions for use, reproduction, and distribution',
        'grant of copyright license',
        'grant of patent license',
        'redistribution. you may reproduce and distribute copies',
        'acceptance of support, warranty, indemnity, or other liability obligations',
        'end of terms and conditions',
    ), ()),
    'BSD-2-Clause': ((
        'redistribution and use in source and binary forms, with or without modification',
        'redistributions of source code must retain the above copyright notice',
        'redistributions in binary form must reproduce the above copyright notice',
        'this software is provided by the copyright holders and contributors "as is"',
    ), (
        'neither the name of the copyright holder nor the names of its contributors',
    )),
    'BSD-3-Clause': ((
        'redistribution and use in source and binary forms, with or without modification',
        'redistributions of source code must retain the above copyright notice',
        'redistributions in binary form must reproduce the above copyright notice',
        'neither the name of the copyright holder nor the names of its contributors',
        'this software is provided by the copyright holders and contributors "as is"',
    ), ()),
    'MPL-2.0': ((
        'mozilla public license version 2.0',
        '1. definitions',
        '2. license grants and conditions',
        '3. responsibilities',
        '10. versions of the license',
        'exhibit a - source code form license notice',
    ), ()),
    'ISC': ((
        'permission to use, copy, modify, and/or distribute this software for any purpose',
        'the above copyright notice and this permission notice appear in all copies',
        'the software is provided "as is" and the author disclaims all warranties',
        'in no event shall the author be liable for any special, direct, indirect, or consequential damages',
    ), ()),
}


LICENSE_MARKERS = frozenset(LICENSE_SIGNATURES)


class ExternalContractError(ValueError):
    """Raised when a GitHub source cannot satisfy the shared snapshot contract."""


def validate_source_identity(source_id: str, url: str) -> None:
    match = GITHUB_URL.fullmatch(url)
    if match is None or source_id.casefold() != (
        f'{match.group(1)}/{match.group(2)}'.casefold()
    ):
        raise ExternalContractError('source id and GitHub url must match')


def validate_ref(ref: str | None) -> None:
    if ref is not None and (
        not ref or ref.startswith('-') or GIT_REF.fullmatch(ref) is None
    ):
        raise ExternalContractError('source ref must be a safe Git argument')
