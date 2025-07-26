# API Mandatory Fields Guide
## `/api/v2.0/order/orderlines` Endpoint

---

## Table of Contents
- [Overview](#overview)
- [Critical Mandatory Fields](#critical-mandatory-fields)
- [Conditionally Mandatory Fields](#conditionally-mandatory-fields)
- [Highly Recommended Fields](#highly-recommended-fields)
- [Field Dependencies](#field-dependencies)
- [Validation Rules Summary](#validation-rules-summary)
- [Working Examples](#working-examples)
- [Common Errors](#common-errors)
- [Testing Checklist](#testing-checklist)

---

## Overview

This guide provides the essential mandatory fields required for successful API calls to the `/api/v2.0/order/orderlines` endpoint in the RecVue Contracts Management System. The fields are categorized by their requirement level and dependency context.

### API Endpoint
- **POST** `/api/v2.0/order/orderlines` - Create new order with order lines
- **PUT** `/api/v2.0/order/orderlines` - Update existing order with order lines

---

## 🔴 Critical Mandatory Fields

These fields are **absolutely required** for the API to function. Missing any of these will result in immediate validation failure.

### Order Header - Always Required

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| **`orderNumber`** | String | Unique order identifier | Required if `hdrReferenceNumber` is blank |
| **`orderType`** | String | Type of order | Must be valid order type in system |
| **`orderCategory`** | String | Order category | Cannot be blank |
| **`businessUnit`** | String | Business unit code | Required - drives currency/defaults |
| **`hdrEffectiveStartDate`** | Date (YYYY-MM-DD) | Order start date | Required - auto-defaulted if missing |
| **`hdrBillToCustAccountNum`** | String | Bill-to customer account | Must be valid customer account |

### Order Line - Always Required

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| **`lineNumber`** | String/Number | Line identifier within order | Must be unique, cannot modify after creation |
| **`lineType`** | String | Type of line item | Required - drives all other field validations |
| **`lineEffectiveStartDate`** | Date (YYYY-MM-DD) | Line start date | Required - cannot be modified after creation |

---

## 🟡 Conditionally Mandatory Fields

These fields become mandatory based on the values of other fields or business rules.

### Order Header - Context Dependent

| Field | Condition | Validation Rule |
|-------|-----------|----------------|
| **`hdrEffectiveEndDate`** | When `hdrEvergreenFlag` = "N" | Required for non-evergreen orders |
| **`hdrEvergreenFlag`** | When provided | Must be "Y" or "N" |

### Order Line - Line Type Dependent

| Field | Line Type Dependency | Validation Rule |
|-------|---------------------|----------------|
| **`itemName`** | Most line types | Required for most line types (business rule dependent) |
| **`quantity`** | All line types | • T_COMMIT_USAGE: Must be zero<br>• Others: NULL/NOTNULL/POSITIVE/NEGATIVE per line type |
| **`unitPrice`** | All line types | Same validation rules as quantity based on line type |
| **`uom`** | All line types | Must match allowed UOM for specific line type |
| **`lineEffectiveEndDate`** | Non-evergreen lines | Required when line is not evergreen |
| **`lineBillingCycle`** | Most line types | Must match allowed values (except "BUY" intent) |
| **`lineBillingFrequency`** | Most line types | Must match allowed values (except "BUY" intent) |
| **`lineInvoicingRule`** | Most line types | Must match allowed values (except "BUY" intent) |

### Unit Price Terms - Both Required Together

| Field | Dependency | Validation |
|-------|------------|------------|
| **`lineUnitPriceTermPeriod`** | When term pricing used | Must be provided with Duration |
| **`lineUnitPriceTermDuration`** | When term pricing used | Must be numeric and positive |

---

## 🟢 Highly Recommended Fields

These fields are typically auto-defaulted but should be explicitly provided for clarity and control.

### Order Header

```json
{
  "hdrCurrency": "US Dollar",              // Auto-defaulted from business unit
  "hdrBillingCycle": "1st Day of Period",  // Auto-defaulted
  "hdrBillingFrequency": "Monthly",        // Auto-defaulted
  "hdrInvoicingRule": "Invoice in Advance", // Recommended
  "priceList": "Standard Price List"       // Must be valid if provided
}
```

### Order Line

```json
{
  "lineBillingChannel": "ATLAS",          // Must be valid billing channel
  "lineDeliveryChannel": "FleetOne",      // Must be valid fulfillment channel
  "itemDescription": "Product description", // Optional but recommended
  "lineEvergreenFlag": "N"                // Should match order evergreen setting
}
```

---

## Field Dependencies

### Critical Dependencies

1. **Line Type → All Line Fields**
   - The `lineType` determines validation rules for quantity, unitPrice, uom, billing settings
   - Different line types have different mandatory field requirements

2. **Business Unit → Financial Defaults**
   - `businessUnit` drives automatic defaulting of:
     - `hdrCurrency`
     - `hdrBillingCycle`
     - `hdrBillingFrequency`

3. **Evergreen Flag → End Dates**
   - If `hdrEvergreenFlag` = "Y": End dates become optional
   - If `hdrEvergreenFlag` = "N": End dates are mandatory

4. **Date Consistency Chain**
   - `hdrEffectiveStartDate` ≤ `lineEffectiveStartDate`
   - `lineEffectiveStartDate` < `lineEffectiveEndDate`
   - `lineEffectiveEndDate` ≤ `hdrEffectiveEndDate` (for non-evergreen)

### Field Inheritance

Order lines inherit certain values from the order header:
- Currency
- Billing cycles and frequencies (if not specified at line level)
- Customer account information (if not overridden)
- Evergreen settings (lines cannot be evergreen if order is not)

---

## Validation Rules Summary

### Cannot Be Modified After Creation
- `lineNumber` - Unique identifier, permanent
- `lineEffectiveStartDate` - Start date is locked after creation

### System Integration Checks
- Cannot modify lines that are part of active bill runs
- Cannot modify lines that are part of active pay runs
- Cannot change end dates for BILLED/PARTIAL_BILLED lines
- Cannot set dates before maximum billed date

### Business Rule Validations
- Customer accounts must exist in system
- Line types must be valid and active
- UOM must match allowed values for line type
- Billing configurations must be compatible
- Date ranges must be logical and consistent

---

## Working Examples

### Minimal Required Example

```json
{
  "orderNumber": "ORD-2024-001",
  "orderType": "Standard Order",
  "orderCategory": "New",
  "businessUnit": "US1 Business Unit",
  "hdrEffectiveStartDate": "2024-01-01",
  "hdrEffectiveEndDate": "2024-12-31",
  "hdrBillToCustAccountNum": "CUST-12345",
  "hdrEvergreenFlag": "N",
  "orderLines": [
    {
      "lineNumber": "1",
      "lineType": "Recurring",
      "lineEffectiveStartDate": "2024-01-01",
      "lineEffectiveEndDate": "2024-12-31",
      "itemName": "Monthly Service",
      "quantity": "1",
      "unitPrice": "100.00",
      "uom": "Each"
    }
  ]
}
```

### Complete Recommended Example

```json
{
  "orderNumber": "ORD-2024-001",
  "orderType": "Standard Order",
  "orderCategory": "New",
  "businessUnit": "US1 Business Unit",
  "description": "Monthly Service Contract",
  "hdrEffectiveStartDate": "2024-01-01",
  "hdrEffectiveEndDate": "2024-12-31",
  "hdrBillToCustAccountNum": "CUST-12345",
  "hdrBillToSiteNumber": "SITE-001",
  "hdrCurrency": "USD",
  "hdrBillingCycle": "1st Day of Period",
  "hdrBillingFrequency": "Monthly",
  "hdrInvoicingRule": "Invoice in Advance",
  "hdrEvergreenFlag": "N",
  "priceList": "Standard Price List",
  "orderLines": [
    {
      "lineNumber": "1",
      "lineType": "Recurring",
      "lineEffectiveStartDate": "2024-01-01",
      "lineEffectiveEndDate": "2024-12-31",
      "itemName": "Monthly Service",
      "itemDescription": "Premium monthly service package",
      "quantity": "1",
      "unitPrice": "100.00",
      "uom": "Each",
      "lineBillingCycle": "1st Day of Period",
      "lineBillingFrequency": "Monthly",
      "lineInvoicingRule": "Invoice in Advance",
      "lineBillingChannel": "ATLAS",
      "lineDeliveryChannel": "Digital",
      "lineEvergreenFlag": "N"
    }
  ]
}
```

### Evergreen Order Example

```json
{
  "orderNumber": "ORD-EVERGREEN-001",
  "orderType": "Subscription",
  "orderCategory": "New",
  "businessUnit": "US1 Business Unit",
  "hdrEffectiveStartDate": "2024-01-01",
  "hdrBillToCustAccountNum": "CUST-12345",
  "hdrEvergreenFlag": "Y",
  "orderLines": [
    {
      "lineNumber": "1",
      "lineType": "Recurring",
      "lineEffectiveStartDate": "2024-01-01",
      "itemName": "Subscription Service",
      "quantity": "1",
      "unitPrice": "50.00",
      "uom": "Each",
      "lineEvergreenFlag": "Y"
    }
  ]
}
```

---

## Common Errors

### Validation Failure Examples

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Order number/Header ReferenceNumber both cannot be blank" | Missing order identifier | Provide either `orderNumber` or `hdrReferenceNumber` |
| "Business Unit cannot be blank" | Missing business unit | Provide valid `businessUnit` value |
| "Line number cannot be blank" | Missing line identifier | Provide unique `lineNumber` for each line |
| "Line type is required" | Missing line type | Provide valid `lineType` |
| "Invalid customer account number" | Invalid customer | Verify `hdrBillToCustAccountNum` exists in system |
| "End Date should be later than Start Date" | Date logic error | Ensure end dates are after start dates |
| "Line Type X can't have Quantity as null" | Line type validation | Check quantity requirements for specific line type |
| "Allowed UoM: [list]" | Invalid UOM | Use UOM from allowed list for the line type |

### HTTP Response Format

**Success Response (200)**
```json
{
  "statusCode": "SUCCESS",
  "message": "Order created successfully",
  "id": "12345"
}
```

**Validation Error Response (400)**
```json
{
  "statusCode": "FAILURE",
  "message": "Validation Failed - lineType: Line type is required | quantity: Line Type Recurring can't have Quantity as null",
  "id": null
}
```

---

## Testing Checklist

### Pre-Request Validation
- [ ] All critical mandatory fields are provided
- [ ] Date formats are YYYY-MM-DD
- [ ] Date ranges are logical (start < end)
- [ ] Customer account exists in system
- [ ] Business unit is valid
- [ ] Line types are valid and active

### Line Type Specific Testing
- [ ] Verify UOM is allowed for the line type
- [ ] Check quantity/unit price requirements
- [ ] Validate billing configuration compatibility
- [ ] Confirm evergreen flag consistency

### System Integration Testing
- [ ] Customer account validation
- [ ] Business unit defaults application
- [ ] Line type validation rules
- [ ] Date range consistency checks

### Error Handling Testing
- [ ] Missing mandatory field responses
- [ ] Invalid value responses
- [ ] Business rule violation responses
- [ ] System constraint violation responses

---

## API Usage Tips

1. **Start Simple**: Use the minimal required example first, then add fields as needed
2. **Line Type First**: Always determine the correct `lineType` before setting other line fields
3. **Date Consistency**: Plan your date ranges carefully - they cannot be easily changed later
4. **Customer Validation**: Verify customer accounts exist before creating orders
5. **Business Unit Impact**: Choose the business unit carefully as it drives many defaults
6. **Testing Strategy**: Test with different line types to understand field requirements

---

**Last Updated**: January 2024  
**API Version**: v2.0  
**Document Version**: 1.0

For detailed validation rules, refer to the complete [Order Validation Documentation](./ORDER_VALIDATION_DOCUMENTATION.md).

