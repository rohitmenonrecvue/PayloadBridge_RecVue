# Order and Order Line Validation Documentation

## Table of Contents
- [Overview](#overview)
- [Validation Architecture](#validation-architecture)
- [Order Header Validations](#order-header-validations)
- [Order Line Validations](#order-line-validations)
- [Validation Implementation](#validation-implementation)
- [Error Handling](#error-handling)
- [Sample JSON Structure](#sample-json-structure)

---

## Overview

This document provides comprehensive validation rules for Order Header and Order Line fields in the RecVue Contracts Management System. The validations are implemented across multiple layers to ensure data integrity and business rule compliance.

## Validation Architecture

The validation system is implemented across four main layers:

1. **Controller Layer**: Basic field validation and authentication
2. **Service Layer**: Business rule validation via `OrderLineValidator` and `ProductWorkbenchValidation`
3. **DAO Layer**: Database constraint validations and system integration checks
4. **Import Layer**: Additional validations during order import process

### Key Validation Classes:
- `OrderLineValidator.java` - Core line validation logic
- `ProductWorkbenchValidation.java` - Business rule validations
- `OrderLineController.java` - REST API validation
- `OrderIfaceServiceImpl.java` - Import validation

---

## Order Header Validations

### Basic Order Information

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`orderNumber`** | • Required if `hdrReferenceNumber` is blank<br>• Must exist in system for updates<br>• Cannot be blank | "Order number/Header ReferenceNumber both cannot be blank" |
| **`orderType`** | • Required field<br>• Must be valid order type in system<br>• Lookup validation | "Invalid order type" |
| **`orderCategory`** | • Required field<br>• Must be valid category | "Order category cannot be blank" |
| **`businessUnit`** | • Required field<br>• Must be valid business unit<br>• Drives currency and legal entity defaults | "Business Unit cannot be blank" |
| **`description`** | • Optional field<br>• No specific validation | - |
| **`dealNumber`** | • Optional field<br>• No specific validation | - |
| **`poNumber`** | • Optional field<br>• No specific validation | - |

### Date Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrEffectiveStartDate`** | • Required field<br>• Must be valid date format<br>• Auto-defaulted if not provided | "Effective start date is required" |
| **`hdrEffectiveEndDate`** | • Must be after start date<br>• Required if `hdrEvergreenFlag` is "N"<br>• Optional for evergreen orders | "End Date should be later than Start Date" |
| **`nextRenewalDate`** | • Optional field<br>• Depends on renewal settings<br>• Must be valid date if provided | "Invalid renewal date" |

### Customer Information

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrBillToCustAccountNum`** | • Required field<br>• Must be valid customer account<br>• Cross-reference validation | "Invalid customer account number" |
| **`hdrBillToSiteNumber`** | • Must be valid site for customer<br>• Site-customer relationship validation | "Invalid bill-to site" |
| **`hdrBillToContactNumber`** | • Must be valid contact for site<br>• Contact-site relationship validation | "Invalid bill-to contact" |
| **`hdrSellToCustAccountNum`** | • Must be valid customer account<br>• Can be different from bill-to customer | "Invalid sell-to customer" |
| **`hdrSellToSiteNumber`** | • Must be valid site for sell-to customer | "Invalid sell-to site" |
| **`hdrSellToContactNumber`** | • Must be valid contact for sell-to site | "Invalid sell-to contact" |

### Billing Configuration

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrBillingCycle`** | • Must be valid billing cycle<br>• Lookup validation against core values<br>• Auto-defaulted based on business unit | "Invalid billing cycle" |
| **`hdrBillingFrequency`** | • Must be valid billing frequency<br>• Lookup validation<br>• Auto-defaulted | "Invalid billing frequency" |
| **`hdrInvoicingRule`** | • Must be valid invoicing rule<br>• Lookup validation | "Invalid invoicing rule" |
| **`hdrInvoiceAdj`** | • Must be between 1-31 (day of month)<br>• Numeric validation | "Invoice adjustment day should be between 1 to 31" |
| **`hdrInterfaceAdj`** | • Must be between 1-31 (day of month)<br>• Numeric validation | "Interface adjustment day should be between 1 to 31" |
| **`hdrInvoiceAdjMonths`** | • Must be valid number<br>• Positive integer | "Invalid invoice adjustment months" |
| **`hdrInterfaceAdjMonths`** | • Must be valid number<br>• Positive integer | "Invalid interface adjustment months" |

### Financial Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrCurrency`** | • Must be valid currency code<br>• ISO currency validation<br>• Auto-defaulted from business unit | "Invalid currency" |
| **`priceList`** | • Must be valid price list<br>• Active price list validation | "Invalid price list" |
| **`hdrPayTermName`** | • Must be valid payment terms<br>• Lookup validation | "Invalid payment terms" |
| **`paymentMethod`** | • Must be valid payment method<br>• Lookup validation | "Invalid payment method" |
| **`agencyDiscount`** | • Must be valid decimal<br>• Percentage validation | "Invalid agency discount" |

### Channel and Delivery

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrDeliveryChannel`** | • Must be valid delivery channel<br>• Lookup validation against FULFILLMENT_CHANNEL | "Invalid delivery channel" |
| **`hdrBillingChannel`** | • Must be valid billing channel<br>• Lookup validation against BILLING_CHANNEL | "Invalid billing channel" |

### Control and Flag Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`hdrEvergreenFlag`** | • Must be "Y" or "N"<br>• Affects end date requirements<br>• Cascades to line-level validations | "Invalid evergreen flag" |
| **`hdrDoNotRenew`** | • Must be "Y" or "N"<br>• Business rule validation | "Invalid do not renew flag" |
| **`hdrRenewFlag`** | • Must be "Y" or "N"<br>• Renewal business rule validation | "Invalid renew flag" |
| **`hdrRefreshFlag`** | • Must be "Y" or "N" if provided | "Invalid refresh flag" |

### Custom Attributes

| Field Pattern | Validation Rules | Error Messages |
|---------------|------------------|----------------|
| **`hdrAttribute1V` - `hdrAttribute25V`** | • Optional string fields<br>• Custom business rules may apply<br>• Context-dependent validation | Custom validation messages |
| **`hdrAttribute1N` - `hdrAttribute15N`** | • Optional numeric fields<br>• Must be valid numbers if provided | "Invalid numeric attribute" |
| **`hdrAttribute1D` - `hdrAttribute15D`** | • Optional date fields<br>• Must be valid dates if provided | "Invalid date attribute" |

---

## Order Line Validations

### Basic Line Information

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineNumber`** | • Required field<br>• Must be unique within order<br>• Cannot be modified after creation<br>• Must be valid BigDecimal | "Line number cannot be blank"<br>"Line number already exists"<br>"Line Start date can not be modified" |
| **`itemName`** | • Required for most line types<br>• Business rule dependent | "Item name is required" |
| **`itemDescription`** | • Optional field<br>• No specific validation | - |
| **`trackingOptions`** | • Optional field<br>• Lookup validation if provided | "Invalid tracking option" |

### Quantity and Pricing

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`quantity`** | • **Line type specific validation:**<br>  - T_COMMIT_USAGE: Must be zero<br>  - Other types: NULL, NOTNULL, ZERO, NOTZERO, POSITIVE, NEGATIVE<br>• Must be valid BigDecimal | "Qty always zero" (for T_COMMIT_USAGE)<br>"Line Type X can't have Quantity as null/zero/negative" |
| **`unitPrice`** | • Same validation rules as quantity<br>• Line type drives validation<br>• Must be valid BigDecimal<br>• UOM conversion validation | "Line Type X should have Unit Price greater than zero" |
| **`uom`** | • **Must match allowed UOM for line type**<br>• Validation from `LineTypesValidation.getUom()`<br>• Split by comma for multiple allowed values<br>• "ANY" bypasses validation | "Allowed UoM: [list of valid UOMs]" |

### Date Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineEffectiveStartDate`** | • **Required field**<br>• Must be within order date range<br>• **Cannot be modified after creation**<br>• Must be before line end date<br>• Format: YYYY-MM-DD | "Line Start Date should be within the Order Date Range"<br>"Line Start date can not be modified" |
| **`lineEffectiveEndDate`** | • Must be after line start date<br>• Must be within order date range (non-evergreen)<br>• **Cannot change if billing status is BILLED/PARTIAL_BILLED**<br>• **Last day of month validation** if required by line type<br>• Cannot modify after billing completion | "End Date should be later than Start Date"<br>"Line End Date should be within the Order Date Range"<br>"End date should be greater than line end date"<br>"Line End Date should be Last day of the month"<br>"End date cannot be changed once the last billing cycle is complete" |

### Line Type and Status

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineType`** | • **Required field**<br>• Must be valid line type in system<br>• **Cannot change from/to "Recurring Fulfillment"**<br>• **Drives all other field validations**<br>• Lookup validation | "Line type is required"<br>"Cannot change Line type from X to Y" |
| **`lineStatus`** | • **Cannot modify if "TERMINATED" or "CANCELED"**<br>• Status transition validation | "Line Already Terminated or Cancelled" |

### Billing Configuration

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineBillingCycle`** | • **Must match allowed values for line type**<br>• Validation from `LineTypesValidation.getBillingCycle()`<br>• **Not validated for "BUY" intent lines**<br>• Manual billing cycle validation<br>• "ANY" bypasses validation | "Allowed Billing Cycle: [list]"<br>"Allowed Billing Cycle: Manual Bill Date" |
| **`lineBillingFrequency`** | • **Must match allowed values for line type**<br>• Validation from `LineTypesValidation.getBillingFrequency()`<br>• **Not validated for "BUY" intent lines**<br>• Manual billing frequency validation | "Allowed Billing Frequency: [list]"<br>"Allowed Billing Frequency: Manual" |
| **`lineInvoicingRule`** | • **Must match allowed values for line type**<br>• Validation from `LineTypesValidation.getInvoicingRule()`<br>• **Not validated for "BUY" intent lines**<br>• Special rule for evergreen + one-time frequency | "Allowed Invoicing Rule: [list]"<br>"Invoicing rule must be ADVANCE for evergreen one-time billing" |

### Adjustment Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineInvoiceAdj`** | • **Must be between 1-31** (day of month)<br>• Valid day validation using `StringUtil.checkForValidDay()` | "Invoice adjustment day should be between 1 to 31" |
| **`lineInterfaceAdj`** | • **Must be between 1-31** (day of month)<br>• Valid day validation | "Interface adjustment day should be between 1 to 31" |
| **`lineInvoiceAdjMonths`** | • Must be valid numeric value<br>• Positive number validation | "Invalid invoice adjustment months" |
| **`interfaceAdjMonths`** | • Must be valid numeric value<br>• Positive number validation | "Invalid interface adjustment months" |

### Channel Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineBillingChannel`** | • **Lookup validation** against "BILLING_CHANNEL"<br>• Must be valid billing channel | "Invalid Billing Channel" |
| **`lineDeliveryChannel`** | • **Lookup validation** against "FULFILLMENT_CHANNEL"<br>• Must be valid fulfillment channel | "Invalid Fulfillment Channel" |
| **`fulfillmentChannelId`** | • Must be valid fulfillment channel ID<br>• Cross-reference validation | "Invalid fulfillment channel ID" |
| **`billingChannelId`** | • **Must be unique billing channel ID**<br>• Uniqueness validation using `validateBillingChannelId()`<br>• Cannot duplicate existing billing reference | "Bill Ref ID already exists" |

### Customer Reference Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineBillToCustAccountNum`** | • Must be valid customer account<br>• Customer existence validation | "Invalid bill-to customer account" |
| **`lineBillToSiteNumber`** | • Must be valid site for customer<br>• Site-customer relationship validation | "Invalid bill-to site number" |
| **`lineBillToContactNumber`** | • Must be valid contact for site<br>• Contact-site relationship validation | "Invalid bill-to contact number" |
| **`lineSellToCustAccountNum`** | • Must be valid customer account<br>• Can be different from bill-to | "Invalid sell-to customer account" |
| **`lineSellToSiteNumber`** | • Must be valid site for sell-to customer | "Invalid sell-to site number" |
| **`lineSellToContactNumber`** | • Must be valid contact for sell-to site | "Invalid sell-to contact number" |

### Financial and Commitment Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`commitAmount`** | • **Not validated for line types:** USAGE, T_COMMIT_USAGE, P_COMMIT<br>• Line type specific rules: NULL, NOTNULL, ZERO, NOTZERO, POSITIVE, NEGATIVE<br>• Must be valid BigDecimal | "Line Type X can't have Commit Amount as null/zero"<br>"Line Type X should have Commit Amount greater than zero" |
| **`overageFee`** | • Optional field<br>• Must be valid BigDecimal if provided | "Invalid overage fee" |
| **`lineDiscount`** | • Must be valid percentage<br>• Decimal validation | "Invalid line discount" |
| **`sellPrice`** | • Must be valid BigDecimal<br>• Pricing validation | "Invalid sell price" |

### Tier Pricing

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`tierPricing`** | • **Validation based on `LineTypesValidation.getAllowTierpricing()`**<br>• If "N", tier pricing not allowed<br>• Tier header ID validation | "Tier Pricing Not Allowed for this Line Type" |
| **`multiDimTierPricing`** | • Multi-dimensional tier pricing validation<br>• Business rule dependent | "Invalid multi-dimensional tier pricing" |

### Unit Price Terms

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineUnitPriceTermPeriod`** | • **Must be provided with Duration**<br>• Lookup validation against "UNIT_TERM_PERIOD"<br>• Both period and duration required together | "Enter Unit Price Term Duration"<br>"Invalid Unit Term Period" |
| **`lineUnitPriceTermDuration`** | • **Must be provided with Period**<br>• **Must be numeric and positive**<br>• `isNumeric()` validation<br>• `BigDecimal > 0` validation | "Enter Unit Price Term Period"<br>"Invalid Unit Price Term Duration"<br>"Please Enter only positive No for Unit Price Term Duration" |

### Evergreen and Control Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`lineEvergreenFlag`** | • **Cannot be "Y" if order evergreen flag is "N"**<br>• Consistency with header evergreen setting<br>• **Special rule:** For one-time billing frequency + evergreen "Y", invoicing rule must be "ADVANCE" | "Order is not evergreen, line cannot be evergreen"<br>"Evergreen line with one-time billing must have advance invoicing rule" |
| **`lineRefreshFlag`** | • Must be "Y" or "N" if provided<br>• Business rule validation | "Invalid refresh flag" |
| **`lineRenewFlag`** | • Must be "Y" or "N" if provided<br>• Renewal business rules | "Invalid renew flag" |

### Rule and Accounting Fields

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **`accountingRule`** | • Must be valid accounting rule<br>• Lookup validation | "Invalid accounting rule" |
| **`ruleStartDate`** | • **Auto-defaulted to `revStartDate` if null**<br>• Must be valid date | "Invalid rule start date" |
| **`ruleEndDate`** | • **Auto-defaulted to `revEndDate` if null**<br>• Must be valid date<br>• Must be after rule start date | "Invalid rule end date" |
| **`lineInvoicingRule`** | • Must be valid invoicing rule<br>• Line type specific validation<br>• Not validated for "BUY" intent | "Invalid invoicing rule" |

### System Integration Validations

| Field/System | Validation Rules | Error Messages |
|--------------|------------------|----------------|
| **Bill Run Status** | • **Cannot modify lines part of active bill runs**<br>• `getBillRunStatus()` validation<br>• Unbilled bill run validation | "Order Lines Update is not allowed when the order is part of Bill run"<br>"Order line is part of bill run: [Bill Run IDs]" |
| **Pay Run Status** | • **Cannot modify lines part of active pay runs**<br>• `getPayRunStatus()` validation | "Order Lines Update is not allowed when the order is part of Pay run" |
| **Billing Status** | • **Restrictions based on BILLED/PARTIAL_BILLED status**<br>• End date change restrictions<br>• Billing completion checks | "Cannot modify billed lines"<br>"Last billing cycle is complete. Hence changes cannot be applied" |
| **Max Billed Date** | • **Database validation via `checkMaxBilledDate()`**<br>• Cannot set dates before maximum billed date | "Line dates cannot be before the maximum billed date" |
| **Multi-Line Billing** | • **Multi-line minimum validation via `checkMLbilled()`**<br>• Line interdependency checks | "Multi-line minimum validation failed" |

### Amendment-Specific Validations

| Context | Validation Rules | Error Messages |
|---------|------------------|----------------|
| **Change Effective Date** | • Cannot be before line start date<br>• Must be within line date range<br>• **Application date validation**<br>• Evergreen vs non-evergreen rules | "Change Effective Date cannot be before the Line Start Date"<br>"Application Date should be within the Line Date Range"<br>"Application Date should be after Line start date" |
| **Pricing Schedule Conflicts** | • Cannot equal existing pricing schedule start dates<br>• Cannot be before last applied pricing schedule<br>• Unit price change validation | "Change Effective Date can not be equal to Pricing Schedules Start Date"<br>"Change Effective Date can be in between last applied Pricing Schedules period but NOT prior to that" |
| **Termination Validations** | • Cannot terminate before line start date<br>• Cannot terminate after line/order end dates<br>• Previous termination date validation<br>• Evergreen termination rules | "Termination Date cannot be before Line Start Date"<br>"Cannot cancel after Line End Date. Please extend Line End Date"<br>"Cannot cancel. The cancel date is after an existing termination date" |

### Custom Attribute Fields

| Field Pattern | Validation Rules | Error Messages |
|---------------|------------------|----------------|
| **`lineAttribute1V` - `lineAttribute25V`** | • Optional string fields<br>• Context-dependent validation<br>• Custom business rules may apply | Custom validation messages |
| **`lineAttribute1N` - `lineAttribute15N`** | • Optional numeric fields<br>• Must be valid BigDecimal if provided | "Invalid numeric line attribute" |
| **`lineAttribute1D` - `lineAttribute15D`** | • Optional date fields<br>• Must be valid dates if provided | "Invalid date line attribute" |
| **`lineTaxAttribute1V` - `lineTaxAttribute30V`** | • Optional tax-related string fields<br>• Tax calculation dependencies | "Invalid tax attribute" |
| **`linePaymentAttribute1V` - `linePaymentAttribute15V`** | • Optional payment-related fields<br>• Payment processing dependencies | "Invalid payment attribute" |
| **`lineRevAttribute1V` - `lineRevAttribute15V`** | • Optional revenue-related fields<br>• Revenue recognition dependencies | "Invalid revenue attribute" |

---

## Validation Implementation

### Validation Flow

1. **Controller Level Validation**
   - `@Valid` annotation processing
   - Field-level validation
   - Authentication and authorization

2. **Service Level Validation**
   - `OrderLineValidator.validateOrderLine()`
   - `ProductWorkbenchValidation.validateOrderLine()`
   - Business rule validation

3. **DAO Level Validation**
   - Database constraint validation
   - Foreign key validation
   - System integration checks

4. **Import Level Validation**
   - Batch processing validation
   - Data transformation validation
   - Error handling and reporting

### Key Validation Methods

```java
// Core validation entry points
OrderLineValidator.validateOrderLine(OrderLines line, AmendmentLineUpdate dto)
ProductWorkbenchValidation.validateOrderLine(OrderLines line, OrderHeader orderHeader)
OrderLineValidator.validateCancelLineEndDtCR(OrderLines line, OrderHeader orderHeader)
ProductWorkbenchValidation.validateUnBilledBillRunStatus(OrderLines line, List<String> validationErr)
```

### Validation Configuration

- **Line Type Validation Setup**: Database-driven validation rules per line type
- **Core Lookup Values**: System-wide validation reference data
- **Business Unit Defaults**: Auto-population based on business unit
- **Custom Validation Rules**: Configurable per implementation

---

## Error Handling

### Error Response Format

```json
{
  "statusCode": "FAILURE",
  "message": "Validation Failed - field: error message | field2: error message2",
  "id": null
}
```

### Common Error Patterns

1. **Field Validation Errors**: "Validation Failed - fieldName: error message"
2. **Business Rule Errors**: Specific business context messages
3. **System Integration Errors**: "Order Lines Update is not allowed when..."
4. **Date Range Errors**: "[Field] should be within the [Range] Date Range"
5. **Lookup Validation Errors**: "Invalid [Field Name]" or "Allowed [Field]: [list]"

### Error Aggregation

The system collects all validation errors and returns them together, allowing users to fix multiple issues in a single iteration.

---

## Sample JSON Structure

### Order Header Sample
```json
{
  "orderNumber": "GSFO48",
  "description": "Testing Order",
  "orderType": "Shell Asia Singapore",
  "orderCategory": "New",
  "businessUnit": "US1 Business Unit",
  "hdrEffectiveStartDate": "2023-01-01",
  "hdrEffectiveEndDate": "2023-01-31",
  "hdrCurrency": "US Dollar",
  "hdrEvergreenFlag": "N",
  "hdrBillToCustAccountNum": "26360",
  "hdrBillingCycle": "1st Day of Period",
  "hdrBillingFrequency": "Monthly",
  "orderLines": []
}
```

### Order Line Sample
```json
{
  "lineNumber": "1",
  "itemName": "Diesel",
  "itemDescription": "Diesel-Desc",
  "uom": "Each",
  "quantity": "10",
  "unitPrice": "20",
  "lineEffectiveStartDate": "2023-01-01",
  "lineEffectiveEndDate": "2023-01-31",
  "lineType": "Recurring",
  "lineBillingCycle": "1st Day of Period",
  "lineBillingFrequency": "Monthly",
  "lineInvoicingRule": "Invoice in Advance",
  "lineEvergreenFlag": "N",
  "lineBillingChannel": "ATLAS",
  "lineDeliveryChannel": "FleetOne"
}
```

---

## Validation Summary

### Critical Validations (Must Pass)
- Order number and business unit presence
- Date range consistency
- Line type compatibility
- Customer account validity
- Billing configuration consistency
- System integration constraints

### Business Rule Validations (Context Dependent)
- Line type specific field requirements
- Evergreen flag cascading rules
- Amendment and termination rules
- Pricing and commitment validation

### Optional Validations (Warning Level)
- Custom attribute validation
- Optional field format validation
- Business process recommendations

---

**Note**: This documentation reflects the validation rules implemented in the RecVue Contracts Management System as of the current version. Business rules may vary based on configuration and customization.

