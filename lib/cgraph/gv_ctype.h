/// \file
/// \brief replacements for ctype.h functions
///
/// The behavior of the ctype.h functions is locale-dependent, while Graphviz
/// code typically wants to ask about character data specifically interpreted as
/// ASCII. The current locale is frequently irrelevant because Graphviz (1)
/// supports input in encodings different than the user’s locale via the
/// `charset` attribute and (2) is often producing output formats that are
/// implicitly ASCII-only.
///
/// This discrepancy leads to misbehavior when trying to use the ctype.h
/// functions as-is. For example, certain Windows environments with a signed
/// `char` type crash when `isdigit` is called with a `char` that is part of a
/// multi-byte unicode character and has its high bit set.
///
/// There are various solutions to this like using a full internationalization
/// library or constructing an ASCII locale and calling the `*_l` variants. But
/// for simplicity we just implement the exact discriminators we need.

#pragma once

#include <stdbool.h>

static inline bool gv_isalpha(int c) {
  if (c >= 'a' && c <= 'z')
    return true;
  if (c >= 'A' && c <= 'Z')
    return true;
  return false;
}

static inline bool gv_isdigit(int c) { return c >= '0' && c <= '9'; }
