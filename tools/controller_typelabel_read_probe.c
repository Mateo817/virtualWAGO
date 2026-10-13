/* Own bounded read client for the original same-board typelabel library.
 * Build with the authentic private header; never publish that header or data.
 * Run only behind the reviewed REG/SYSFS/RO namespace and open mediator.
 * No DAL, I/O master, identity replacement or raw field logging.
 */
#include <typelabel_API.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

int main(void) {
  char *marking = typelabel_QUICK_GetValue("MARKING");
  char *maximum = typelabel_QUICK_GetValue("MAXTERM");
  bool marking_valid = marking != NULL && strcmp(marking, "PFC") == 0;
  bool maximum_present = maximum != NULL;
  bool maximum_nonempty = maximum_present && maximum[0] != '\0';
  bool maximum_decimal = maximum_nonempty;
  if (maximum != NULL) {
    const char *digits = maximum;
    for (; maximum_decimal && *digits != '\0'; ++digits)
      if (*digits < '0' || *digits > '9') maximum_decimal = false;
  }
  if (marking != NULL) typelabel_QUICK_FreeValue(marking);
  if (maximum != NULL) typelabel_QUICK_FreeValue(maximum);

  /* Mirrors the native signature reader's default New/Open/Sync path using
   * the original opaque object. Presence is measured; values stay in-process.
   * This is not execution or acceptance of the runtime's signature check.
   */
  tTypeLabel label = typelabel_OBJECT_New();
  bool synchronized = label != NULL &&
      typelabel_OBJECT_Open(label) == TYPELABEL_RETURN_OK &&
      typelabel_OBJECT_Sync(label) == TYPELABEL_RETURN_OK;
  const char *fields[] = {"DEVICEID", "SIGN", "VENDORID", "DEVICEMASK",
                          "WAGONRSTR", "SYSDESC"};
  unsigned present = 0u;
  bool field_present[6] = {false};
  bool field_nonempty[6] = {false};
  if (synchronized) {
    for (unsigned i = 0u; i < sizeof(fields) / sizeof(fields[0]); ++i) {
      char *value = typelabel_OBJECT_GetValue(label, fields[i]);
      field_present[i] = value != NULL;
      field_nonempty[i] = field_present[i] && value[0] != '\0';
      if (field_present[i]) ++present;
      if (value != NULL) typelabel_OBJECT_FreeValue(value);
    }
  }
  if (label != NULL) typelabel_OBJECT_Destroy(label);
  /* Native MAXTERM uses base-0 strtoul and a parsed-zero fallback. Decimal
   * formatting and six nonempty fields are not its acceptance criteria.
   * Only the unchanged runtime can qualify its full target/signature check.
   */
  bool read_completed = synchronized;
  printf("{\"scope\":\"original same-board typelabel read client only\","
         "\"marking_matches_pfc\":%u,\"maximum_present\":%u,"
         "\"maximum_nonempty\":%u,\"maximum_decimal_format\":%u,\"synchronized\":%u,"
         "\"signature_fields_present\":%u,"
         "\"field_present\":[%u,%u,%u,%u,%u,%u],"
         "\"field_nonempty\":[%u,%u,%u,%u,%u,%u],\"read_completed\":%u}\n",
         (unsigned)marking_valid, (unsigned)maximum_present,
         (unsigned)maximum_nonempty, (unsigned)maximum_decimal, (unsigned)synchronized, present,
         (unsigned)field_present[0], (unsigned)field_present[1],
         (unsigned)field_present[2], (unsigned)field_present[3],
         (unsigned)field_present[4], (unsigned)field_present[5],
         (unsigned)field_nonempty[0], (unsigned)field_nonempty[1],
         (unsigned)field_nonempty[2], (unsigned)field_nonempty[3],
         (unsigned)field_nonempty[4], (unsigned)field_nonempty[5],
         (unsigned)read_completed);
  return read_completed ? 0 : 1;
}
