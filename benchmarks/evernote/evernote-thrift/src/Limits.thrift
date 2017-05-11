/*
 * Copyright 2007-2013 Evernote Corporation.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * This file contains the allowable limits for the various fields and
 * collections that make up the EDAM data model.
 */

namespace as3 com.evernote.edam.limits
namespace java com.evernote.edam.limits
namespace csharp Evernote.EDAM.Limits
namespace py evernote.edam.limits
namespace cpp evernote.limits
namespace rb Evernote.EDAM.Limits
namespace php EDAM.Limits
namespace cocoa EDAM
namespace perl EDAMLimits


// ========================== string field limits ==============================

/**
 * Minimum length of any string-based attribute, in Unicode chars
 */
const i32    EDAM_ATTRIBUTE_LEN_MIN = 1;
/**
 * Maximum length of any string-based attribute, in Unicode chars
 */
const i32    EDAM_ATTRIBUTE_LEN_MAX = 4096;
/**
 * Any string-based attribute must match the provided regular expression.
 * This excludes all Unicode line endings and control characters.
 */
const string EDAM_ATTRIBUTE_REGEX = "^[^\\p{Cc}\\p{Zl}\\p{Zp}]{1,4096}$";

/**
 * The maximum number of values that can be stored in a list-based attribute
 * (e.g. see UserAttributes.recentMailedAddresses)
 */
const i32    EDAM_ATTRIBUTE_LIST_MAX = 100;

/**
 * The maximum number of entries that can be stored in a map-based attribute
 * such as applicationData fields in Resources and Notes.
 */
const i32    EDAM_ATTRIBUTE_MAP_MAX = 100;

/**
 * The minimum length of a GUID generated by the Evernote service
 */
const i32    EDAM_GUID_LEN_MIN = 36;
/**
 * The maximum length of a GUID generated by the Evernote service
 */
const i32    EDAM_GUID_LEN_MAX = 36;
/**
 * GUIDs generated by the Evernote service will match the provided pattern
 */
const string EDAM_GUID_REGEX =
  "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$";

/**
 * The minimum length of any email address
 */
const i32    EDAM_EMAIL_LEN_MIN = 6;
/**
 * The maximum length of any email address
 */
const i32    EDAM_EMAIL_LEN_MAX = 255;
/**
 * A regular expression that matches the part of an email address before
 * the '@' symbol.
 */
const string EDAM_EMAIL_LOCAL_REGEX =
  "^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(\\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*$";
/**
 * A regular expression that matches the part of an email address after
 * the '@' symbol.
 */
const string EDAM_EMAIL_DOMAIN_REGEX =
  "^[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*\\.([A-Za-z]{2,})$";
/**
 * A regular expression that must match any email address given to Evernote.
 * Email addresses must comply with RFC 2821 and 2822.
 */
const string EDAM_EMAIL_REGEX =
  "^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(\\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*\\.([A-Za-z]{2,})$";

/**
 * A regular expression that must match any VAT ID given to Evernote.
 * ref http://en.wikipedia.org/wiki/VAT_identification_number
 * ref http://my.safaribooksonline.com/book/programming/regular-expressions/9780596802837/4dot-validation-and-formatting/id2995136 
 */
const string EDAM_VAT_REGEX =
  "^((AT)?U[0-9]{8}|(BE)?0?[0-9]{9}|(BG)?[0-9]{9,10}|(CY)?[0-9]{8}L|(CZ)?[0-9]{8,10}|(DE)?[0-9]{9}|(DK)?[0-9]{8}|(EE)?[0-9]{9}|(EL|GR)?[0-9]{9}|(ES)?[0-9A-Z][0-9]{7}[0-9A-Z]|(FI)?[0-9]{8}|(FR)?[0-9A-Z]{2}[0-9]{9}|(GB)?([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})|(HU)?[0-9]{8}|(IE)?[0-9]S[0-9]{5}L|(IT)?[0-9]{11}|(LT)?([0-9]{9}|[0-9]{12})|(LU)?[0-9]{8}|(LV)?[0-9]{11}|(MT)?[0-9]{8}|(NL)?[0-9]{9}B[0-9]{2}|(PL)?[0-9]{10}|(PT)?[0-9]{9}|(RO)?[0-9]{2,10}|(SE)?[0-9]{12}|(SI)?[0-9]{8}|(SK)?[0-9]{10})|[0-9]{9}MVA|[0-9]{6}|CHE[0-9]{9}(TVA|MWST|IVA)$";

/**
 * The minimum length of a timezone specification string
 */
const i32    EDAM_TIMEZONE_LEN_MIN = 1;
/**
 * The maximum length of a timezone specification string
 */
const i32    EDAM_TIMEZONE_LEN_MAX = 32;
/**
 * Any timezone string given to Evernote must match the provided pattern.
 * This permits either a locale-based standard timezone or a GMT offset.
 * E.g.:<ul>
 *    <li>America/Los_Angeles</li>
 *    <li>GMT+08:00</li>
 * </ul>
 */
const string EDAM_TIMEZONE_REGEX =
  "^([A-Za-z_-]+(/[A-Za-z_-]+)*)|(GMT(-|\\+)[0-9]{1,2}(:[0-9]{2})?)$";

/**
 * The minimum length of any MIME type string given to Evernote
 */
const i32    EDAM_MIME_LEN_MIN = 3;
/**
 * The maximum length of any MIME type string given to Evernote
 */
const i32    EDAM_MIME_LEN_MAX = 255;
/**
 * Any MIME type string given to Evernote must match the provided pattern.
 * E.g.:  image/gif
 */
const string EDAM_MIME_REGEX = "^[A-Za-z]+/[A-Za-z0-9._+-]+$";

/** Canonical MIME type string for GIF image resources */
const string EDAM_MIME_TYPE_GIF = "image/gif";
/** Canonical MIME type string for JPEG image resources */
const string EDAM_MIME_TYPE_JPEG = "image/jpeg";
/** Canonical MIME type string for PNG image resources */
const string EDAM_MIME_TYPE_PNG = "image/png";
/** Canonical MIME type string for WAV audio resources */
const string EDAM_MIME_TYPE_WAV = "audio/wav";
/** Canonical MIME type string for MP3 audio resources */
const string EDAM_MIME_TYPE_MP3 = "audio/mpeg";
/** Canonical MIME type string for AMR audio resources */
const string EDAM_MIME_TYPE_AMR = "audio/amr";
/** Canonical MIME type string for AAC audio resources */
const string EDAM_MIME_TYPE_AAC = "audio/aac";
/** Canonical MIME type string for MP4 audio resources */
const string EDAM_MIME_TYPE_M4A = "audio/mp4";
/** Canonical MIME type string for MP4 video resources */
const string EDAM_MIME_TYPE_MP4_VIDEO = "video/mp4";
/** Canonical MIME type string for Evernote Ink resources */
const string EDAM_MIME_TYPE_INK = "application/vnd.evernote.ink";
/** Canonical MIME type string for PDF resources */
const string EDAM_MIME_TYPE_PDF = "application/pdf";
/** MIME type used for attachments of an unspecified type */
const string EDAM_MIME_TYPE_DEFAULT = "application/octet-stream";

/**
 * The set of resource MIME types that are expected to be handled
 * correctly by all of the major Evernote client applications.
 */
const set<string> EDAM_MIME_TYPES = [
  EDAM_MIME_TYPE_GIF,
  EDAM_MIME_TYPE_JPEG,
  EDAM_MIME_TYPE_PNG,
  EDAM_MIME_TYPE_WAV,
  EDAM_MIME_TYPE_MP3,
  EDAM_MIME_TYPE_AMR,
  EDAM_MIME_TYPE_INK,
  EDAM_MIME_TYPE_PDF,
  EDAM_MIME_TYPE_MP4_VIDEO,
  EDAM_MIME_TYPE_AAC,
  EDAM_MIME_TYPE_M4A
];

/**
 * The set of MIME types that Evernote will parse and index for
 * searching. With exception of images, and PDFs, which are
 * handled in a different way.
 */
const set<string> EDAM_INDEXABLE_RESOURCE_MIME_TYPES = [
  "application/msword",
  "application/mspowerpoint",
  "application/excel",
  "application/vnd.ms-word",
  "application/vnd.ms-powerpoint",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.apple.pages",
  "application/vnd.apple.numbers",
  "application/vnd.apple.keynote",
  "application/x-iwork-pages-sffpages",
  "application/x-iwork-numbers-sffnumbers",
  "application/x-iwork-keynote-sffkey"
];

/**
 * The minimum length of a user search query string in Unicode chars
 */
const i32    EDAM_SEARCH_QUERY_LEN_MIN = 0;
/**
 * The maximum length of a user search query string in Unicode chars
 */
const i32    EDAM_SEARCH_QUERY_LEN_MAX = 1024;
/**
 * Search queries must match the provided pattern.  This is used for
 * both ad-hoc queries and SavedSearch.query fields.
 * This excludes all control characters and line/paragraph separators.
 */
const string EDAM_SEARCH_QUERY_REGEX = "^[^\\p{Cc}\\p{Zl}\\p{Zp}]{0,1024}$";

/**
 * The exact length of a MD5 hash checksum, in binary bytes.
 * This is the exact length that must be matched for any binary hash
 * value.
 */
const i32    EDAM_HASH_LEN = 16;

/**
 * The minimum length of an Evernote username
 */
const i32    EDAM_USER_USERNAME_LEN_MIN = 1;
/**
 * The maximum length of an Evernote username
 */
const i32    EDAM_USER_USERNAME_LEN_MAX = 64;
/**
 * Any Evernote User.username field must match this pattern.  This
 * restricts usernames to a format that could permit use as a domain
 * name component.  E.g. "username.whatever.evernote.com"
 */
const string EDAM_USER_USERNAME_REGEX = "^[a-z0-9]([a-z0-9_-]{0,62}[a-z0-9])?$";

/**
 * Minimum length of the User.name field
 */
const i32    EDAM_USER_NAME_LEN_MIN = 1;
/**
 * Maximum length of the User.name field
 */
const i32    EDAM_USER_NAME_LEN_MAX = 255;
/**
 * The User.name field must match this pattern, which excludes line
 * endings and control characters.
 */
const string EDAM_USER_NAME_REGEX = "^[^\\p{Cc}\\p{Zl}\\p{Zp}]{1,255}$";

/**
 * The minimum length of a Tag.name, in Unicode characters
 */
const i32    EDAM_TAG_NAME_LEN_MIN = 1;
/**
 * The maximum length of a Tag.name, in Unicode characters
 */
const i32    EDAM_TAG_NAME_LEN_MAX = 100;
/**
 * All Tag.name fields must match this pattern.
 * This excludes control chars, commas or line/paragraph separators.
 * The string may not begin or end with whitespace.
 */
const string EDAM_TAG_NAME_REGEX =
  "^[^,\\p{Cc}\\p{Z}]([^,\\p{Cc}\\p{Zl}\\p{Zp}]{0,98}[^,\\p{Cc}\\p{Z}])?$";

/**
 * The minimum length of a Note.title, in Unicode characters
 */
const i32    EDAM_NOTE_TITLE_LEN_MIN = 1;
/**
 * The maximum length of a Note.title, in Unicode characters
 */
const i32    EDAM_NOTE_TITLE_LEN_MAX = 255;
/**
 * All Note.title fields must match this pattern.
 * This excludes control chars or line/paragraph separators.
 * The string may not begin or end with whitespace.
 */
const string EDAM_NOTE_TITLE_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,253}[^\\p{Cc}\\p{Z}])?$";

/**
 * Minimum length of a Note.content field.
 * Note.content fields must comply with the ENML DTD.
 */
const i32    EDAM_NOTE_CONTENT_LEN_MIN = 0;
/**
 * Maximum length of a Note.content field
 * Note.content fields must comply with the ENML DTD.
 */
const i32    EDAM_NOTE_CONTENT_LEN_MAX = 5242880;

/**
 * Minimum length of an application name, which is the key in an
 * applicationData LazyMap found in entities such as Resources and
 * Notes.
 */
const i32    EDAM_APPLICATIONDATA_NAME_LEN_MIN = 3;
/**
 * Maximum length of an application name, which is the key in an
 * applicationData LazyMap found in entities such as Resources and
 * Notes.
 */
const i32    EDAM_APPLICATIONDATA_NAME_LEN_MAX = 32;
/**
 * Minimum length of an applicationData value in a LazyMap, found
 * in entities such as Resources and Notes.
 */
const i32    EDAM_APPLICATIONDATA_VALUE_LEN_MIN = 0;
/**
 * Maximum length of an applicationData value in a LazyMap, found
 * in entities such as Resources and Notes.  Note, however, that
 * the sum of the size of hte key and value is constrained by
 * EDAM_APPLICATIONDATA_ENTRY_LEN_MAX, so the maximum length, in
 * practice, depends upon the key value being used.
 */
const i32    EDAM_APPLICATIONDATA_VALUE_LEN_MAX = 4092;
/**
 * The total length of an entry in an applicationData LazyMap, which
 * is the sum of the length of the key and the value for the entry.
 */
const i32    EDAM_APPLICATIONDATA_ENTRY_LEN_MAX = 4095;
/**
 * An application name must match this regex.  An application
 * name is the key portion of an entry in an applicationData
 * map as found in entities such as Resources and Notes.
 * Note that even if both the name and value regexes match,
 * it is still necessary to check the sum of the lengths
 * against EDAM_APPLICATIONDATA_ENTRY_LEN_MAX.
 */
const string EDAM_APPLICATIONDATA_NAME_REGEX = "^[A-Za-z0-9_.-]{3,32}$";
/**
 * An applicationData map value must match this regex.
 * Note that even if both the name and value regexes match,
 * it is still necessary to check the sum of the lengths
 * against EDAM_APPLICATIONDATA_ENTRY_LEN_MAX.
 */
const string EDAM_APPLICATIONDATA_VALUE_REGEX = "^[^\\p{Cc}]{0,4092}$";

/**
 * The minimum length of a Notebook.name, in Unicode characters
 */
const i32    EDAM_NOTEBOOK_NAME_LEN_MIN = 1;
/**
 * The maximum length of a Notebook.name, in Unicode characters
 */
const i32    EDAM_NOTEBOOK_NAME_LEN_MAX = 100;
/**
 * All Notebook.name fields must match this pattern.
 * This excludes control chars or line/paragraph separators.
 * The string may not begin or end with whitespace.
 */
const string EDAM_NOTEBOOK_NAME_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,98}[^\\p{Cc}\\p{Z}])?$";

/**
 * The minimum length of a Notebook.stack, in Unicode characters
 */
const i32    EDAM_NOTEBOOK_STACK_LEN_MIN = 1;
/**
 * The maximum length of a Notebook.stack, in Unicode characters
 */
const i32    EDAM_NOTEBOOK_STACK_LEN_MAX = 100;
/**
 * All Notebook.stack fields must match this pattern.
 * This excludes control chars or line/paragraph separators.
 * The string may not begin or end with whitespace.
 */
const string EDAM_NOTEBOOK_STACK_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,98}[^\\p{Cc}\\p{Z}])?$";

/**
 * The minimum length of a public notebook URI component
 */
const i32    EDAM_PUBLISHING_URI_LEN_MIN = 1;
/**
 * The maximum length of a public notebook URI component
 */
const i32    EDAM_PUBLISHING_URI_LEN_MAX = 255;
/**
 * A public notebook URI component must match the provided pattern
 */
const string EDAM_PUBLISHING_URI_REGEX = "^[a-zA-Z0-9.~_+-]{1,255}$";
/**
 * The set of strings that may not be used as a publishing URI
 */
const set<string> EDAM_PUBLISHING_URI_PROHIBITED = [ ".." ];

/**
 * The minimum length of a Publishing.publicDescription field.
 */
const i32    EDAM_PUBLISHING_DESCRIPTION_LEN_MIN = 1;
/**
 * The maximum length of a Publishing.publicDescription field.
 */
const i32    EDAM_PUBLISHING_DESCRIPTION_LEN_MAX = 200;
/**
 * Any public notebook's Publishing.publicDescription field must match
 * this pattern.
 * No control chars or line/paragraph separators, and can't start or
 * end with whitespace.
 */
const string EDAM_PUBLISHING_DESCRIPTION_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,198}[^\\p{Cc}\\p{Z}])?$";

/**
 * The minimum length of a SavedSearch.name field
 */
const i32    EDAM_SAVED_SEARCH_NAME_LEN_MIN = 1;
/**
 * The maximum length of a SavedSearch.name field
 */
const i32    EDAM_SAVED_SEARCH_NAME_LEN_MAX = 100;
/**
 * SavedSearch.name fields must match this pattern.
 * No control chars or line/paragraph separators, and can't start or
 * end with whitespace.
 */
const string EDAM_SAVED_SEARCH_NAME_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,98}[^\\p{Cc}\\p{Z}])?$";

/**
 * The minimum length of an Evernote user password
 */
const i32    EDAM_USER_PASSWORD_LEN_MIN = 6;
/**
 * The maximum length of an Evernote user password
 */
const i32    EDAM_USER_PASSWORD_LEN_MAX = 64;
/**
 * Evernote user passwords must match this regular expression
 */
const string EDAM_USER_PASSWORD_REGEX =
  "^[A-Za-z0-9!#$%&'()*+,./:;<=>?@^_`{|}~\\[\\]\\\\-]{6,64}$";

/**
 * The maximum length of an Evernote Business URI
 */
const i32    EDAM_BUSINESS_URI_LEN_MAX = 32;

// ==================== data model collection limits ===========================

/**
 * The maximum number of Tags per Note
 */
const i32    EDAM_NOTE_TAGS_MAX = 100;

/**
 * The maximum number of Resources per Note
 */
const i32    EDAM_NOTE_RESOURCES_MAX = 1000;

/**
 * Maximum number of Tags per account
 */
const i32    EDAM_USER_TAGS_MAX = 100000;

/**
 * Maximum number of Tags per business account.
 */
const i32    EDAM_BUSINESS_TAGS_MAX = 100000;

/**
 * Maximum number of SavedSearches per account
 */
const i32    EDAM_USER_SAVED_SEARCHES_MAX = 100;

/**
 * Maximum number of Notes per user
 */
const i32    EDAM_USER_NOTES_MAX = 100000;

/**
 * Maximum number of Notes per business account
 */
const i32    EDAM_BUSINESS_NOTES_MAX = 500000;

/**
 * Maximum number of Notebooks per user
 */
const i32    EDAM_USER_NOTEBOOKS_MAX = 250;

/**
 * Maximum number of Notebooks in a business account
 */
const i32    EDAM_BUSINESS_NOTEBOOKS_MAX = 5000;

/**
 * Maximum number of recent email addresses that are maintained
 * (see UserAttributes.recentMailedAddresses)
 */
const i32    EDAM_USER_RECENT_MAILED_ADDRESSES_MAX = 10;

/**
 * The number of emails of any type that can be sent by a user with a Free
 * account from the service per day.  If an email is sent to two different
 * recipients, this counts as two emails.
 */
const i32    EDAM_USER_MAIL_LIMIT_DAILY_FREE = 50;

/**
 * The number of emails of any type that can be sent by a user with a Premium
 * account from the service per day.  If an email is sent to two different
 * recipients, this counts as two emails.
 */
const i32    EDAM_USER_MAIL_LIMIT_DAILY_PREMIUM = 200;

/**
 * The number of bytes of new data that may be uploaded to a Free user's
 * account each month.
 */
const i64    EDAM_USER_UPLOAD_LIMIT_FREE = 62914560;

/**
 * The number of bytes of new data that may be uploaded to a Premium user's
 * account each month.
 */
const i64    EDAM_USER_UPLOAD_LIMIT_PREMIUM = 1073741824;

/**
 * The number of bytes of new data that may be uploaded to a Business user's
 * personal account each month. Note that content uploaded into the Business
 * notebooks by the user does not count against this limit.
 */
const i64    EDAM_USER_UPLOAD_LIMIT_BUSINESS = 2147483647;

/**
 * Maximum total size of a Note that can be added to a Free account.
 * The size of a note is calculated as:
 * ENML content length (in Unicode characters) plus the sum of all resource
 * sizes (in bytes).
 */
const i32    EDAM_NOTE_SIZE_MAX_FREE = 26214400;

/**
 * Maximum total size of a Note that can be added to a Premium account.
 * The size of a note is calculated as:
 * ENML content length (in Unicode characters) plus the sum of all resource
 * sizes (in bytes).
 */
const i32    EDAM_NOTE_SIZE_MAX_PREMIUM = 104857600;

/**
 * Maximum size of a resource, in bytes, for Free accounts
 */
const i32    EDAM_RESOURCE_SIZE_MAX_FREE = 26214400;

/**
 * Maximum size of a resource, in bytes, for Premium accounts
 */
const i32    EDAM_RESOURCE_SIZE_MAX_PREMIUM = 104857600;

/**
 * Maximum number of linked notebooks per account, for a free
 * account.
 */
const i32   EDAM_USER_LINKED_NOTEBOOK_MAX = 100;

/**
 * Maximum number of linked notebooks per account, for a premium
 * account.  Users who are part of an active business are also
 * covered under "premium".
 */
const i32   EDAM_USER_LINKED_NOTEBOOK_MAX_PREMIUM = 250;

/**
 * Maximum number of shared notebooks per notebook
 */
const i32   EDAM_NOTEBOOK_SHARED_NOTEBOOK_MAX = 250;

/**
 * The minimum length of the content class attribute of a note.
 */
const i32   EDAM_NOTE_CONTENT_CLASS_LEN_MIN = 3;

/**
 * The maximum length of the content class attribute of a note.
 */
const i32   EDAM_NOTE_CONTENT_CLASS_LEN_MAX = 32;

/**
 * The regular expression that the content class of a note must match
 * to be valid.
 */
const string EDAM_NOTE_CONTENT_CLASS_REGEX = "^[A-Za-z0-9_.-]{3,32}$";

/**
 * The content class prefix used for all notes created by Evernote Hello.
 * This prefix can be used to assemble individual content class strings,
 * or can be used to create a wildcard search to get all notes created by
 * Hello. When performing a wildcard search via filtered sync chunks or
 * search strings, the * character must be appended to this constant.
 */
const string EDAM_HELLO_APP_CONTENT_CLASS_PREFIX = "evernote.hello.";

/**
 * The content class prefix used for all notes created by Evernote Food.
 * This prefix can be used to assemble individual content class strings,
 * or can be used to create a wildcard search to get all notes created by
 * Food. When performing a wildcard search via filtered sync chunks or
 * search strings, the * character must be appended to this constant.
 */
const string EDAM_FOOD_APP_CONTENT_CLASS_PREFIX = "evernote.food.";

/**
 * The content class prefix used for structured notes created by Evernote
 * Hello that represents an encounter with a person. When performing a
 * wildcard search via filtered sync chunks or search strings, the *
 * character must be appended to this constant.
 */
const string EDAM_CONTENT_CLASS_HELLO_ENCOUNTER = "evernote.hello.encounter";

/**
 * The content class prefix used for structured notes created by Evernote
 * Hello that represents the user's profile. When performing a
 * wildcard search via filtered sync chunks or search strings, the *
 * character must be appended to this constant.
 */
const string EDAM_CONTENT_CLASS_HELLO_PROFILE = "evernote.hello.profile";

/**
 * The content class prefix used for structured notes created by
 * Evernote Food that captures the experience of a particular meal.
 * When performing a wildcard search via filtered sync chunks or search
 * strings, the * character must be appended to this constant.
 */
const string EDAM_CONTENT_CLASS_FOOD_MEAL = "evernote.food.meal";

/**
 * The content class prefix used for structured notes created by Evernote
 * Skitch. When performing a wildcard search via filtered sync chunks
 * or search strings, the * character must be appended to this constant.
 */
const string EDAM_CONTENT_CLASS_SKITCH_PREFIX = "evernote.skitch";

/**
 * The content class value used for structured image notes created by Evernote
 * Skitch.
 */
const string EDAM_CONTENT_CLASS_SKITCH = "evernote.skitch";

/**
 * The content class value used for structured PDF notes created by Evernote
 * Skitch.
 */
const string EDAM_CONTENT_CLASS_SKITCH_PDF = "evernote.skitch.pdf";

/**
 * The content class prefix used for structured notes created by Evernote
 * Penultimate. When performing a wildcard search via filtered sync chunks
 * or search strings, the * character must be appended to this constant.
 */
const string EDAM_CONTENT_CLASS_PENULTIMATE_PREFIX = "evernote.penultimate.";

/**
 * The content class value used for structured notes created by Evernote
 * Penultimate that represents a Penultimate notebook.
 */
const string EDAM_CONTENT_CLASS_PENULTIMATE_NOTEBOOK = "evernote.penultimate.notebook";

/**
 * The minimum length of the plain text in a findRelated query, assuming that
 * plaintext is being provided.
 */
const i32 EDAM_RELATED_PLAINTEXT_LEN_MIN = 1;

/**
 * The maximum length of the plain text in a findRelated query, assuming that
 * plaintext is being provided.
 */
const i32 EDAM_RELATED_PLAINTEXT_LEN_MAX = 131072;

/**
 * The maximum number of notes that will be returned from a findRelated()
 * query.
 */
const i32 EDAM_RELATED_MAX_NOTES = 25;

/**
 * The maximum number of notebooks that will be returned from a findRelated()
 * query.
 */
const i32 EDAM_RELATED_MAX_NOTEBOOKS = 1;

/**
 * The maximum number of tags that will be returned from a findRelated() query.
 */
const i32 EDAM_RELATED_MAX_TAGS = 25;

/**
 * The minimum length, in Unicode characters, of a description for a business
 * notebook.
 */
const i32 EDAM_BUSINESS_NOTEBOOK_DESCRIPTION_LEN_MIN = 1;

/**
 * The maximum length, in Unicode characters, of a description for a business
 * notebook.
 */
const i32 EDAM_BUSINESS_NOTEBOOK_DESCRIPTION_LEN_MAX = 200;
/**
 * All business notebook descriptions must match this pattern.
 * This excludes control chars or line/paragraph separators.
 * The string may not begin or end with whitespace.
 */
const string EDAM_BUSINESS_NOTEBOOK_DESCRIPTION_REGEX =
  "^[^\\p{Cc}\\p{Z}]([^\\p{Cc}\\p{Zl}\\p{Zp}]{0,198}[^\\p{Cc}\\p{Z}])?$";

/**
 * The maximum length of a business phone number.
 */
const i32 EDAM_BUSINESS_PHONE_NUMBER_LEN_MAX = 20;

/**
 * Minimum length of a preference name
 */
const i32 EDAM_PREFERENCE_NAME_LEN_MIN = 3;
/**
 * Maximum length of a preference name
 */
const i32 EDAM_PREFERENCE_NAME_LEN_MAX = 32;
/**
 * Minimum length of a preference value
 */
const i32 EDAM_PREFERENCE_VALUE_LEN_MIN = 1;
/**
 * Maximum length of a preference value
 */
const i32 EDAM_PREFERENCE_VALUE_LEN_MAX = 1024;
/**
 * Maximum number of name/value pairs allowed
 */
const i32 EDAM_MAX_PREFERENCES = 100;
/**
 * Maximum number of values per preference name
 */
const i32 EDAM_MAX_VALUES_PER_PREFERENCE = 256;
/**
 * A preference name must match this regex.
 */
const string EDAM_PREFERENCE_NAME_REGEX = "^[A-Za-z0-9_.-]{3,32}$";
/**
 * A preference value must match this regex.
 */
const string EDAM_PREFERENCE_VALUE_REGEX = "^[^\\p{Cc}]{1,1024}$";
/**
 * The name of the preferences entry that contains shortcuts.
 */
const string EDAM_PREFERENCE_SHORTCUTS = "evernote.shortcuts";
/**
 * The maximum number of shortcuts that a user may have.
 */
const i32 EDAM_PREFERENCE_SHORTCUTS_MAX_VALUES = 250;
/**
 * Maximum length of the device identifier string associated with long sessions.
 */
const i32 EDAM_DEVICE_ID_LEN_MAX = 32;
/**
 * Regular expression for device identifier strings associated with long sessions.
 */
const string EDAM_DEVICE_ID_REGEX = "^[^\\p{Cc}]{1,32}$";
/**
 * Maximum length of the device description string associated with long sessions.
 */
const i32 EDAM_DEVICE_DESCRIPTION_LEN_MAX = 64;
/**
 * Regular expression for device description strings associated with long sessions.
 */
const string EDAM_DEVICE_DESCRIPTION_REGEX = "^[^\\p{Cc}]{1,64}$";

/**
 * Maximum number of search suggestions that can be returned
 */
const i32 EDAM_SEARCH_SUGGESTIONS_MAX = 10;

/**
 * Maximum length of the search suggestion prefix
 */
const i32 EDAM_SEARCH_SUGGESTIONS_PREFIX_LEN_MAX = 1024;

/**
 * Minimum length of the search suggestion prefix
 */
const i32 EDAM_SEARCH_SUGGESTIONS_PREFIX_LEN_MIN = 2;