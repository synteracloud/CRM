const { randomUUID } = require('crypto');

const quotes = new Map();
const orders = new Map();

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function toMoney(value) {
  return Number(Number(value || 0).toFixed(2));
}

function computeQuotePricing(line_items = [], tax_percent = 0) {
  const normalizedTaxPercent = Number(tax_percent || 0);

  const pricedLineItems = line_items.map((lineItem, index) => {
    const quantity = Number(lineItem.quantity || 0);
    const listPrice = Number(lineItem.list_price || 0);
    const discountPercent = Number(lineItem.discount_percent || 0);
    const gross = quantity * listPrice;
    const discountAmount = gross * (discountPercent / 100);
    const netPrice = gross - discountAmount;

    return {
      quote_line_item_id: lineItem.quote_line_item_id || `qli_${index + 1}`,
      product_id: lineItem.product_id,
      quantity,
      list_price: toMoney(listPrice),
      discount_percent: toMoney(discountPercent),
      net_price: toMoney(netPrice),
    };
  });

  const subtotal = toMoney(pricedLineItems.reduce((total, item) => total + item.quantity * item.list_price, 0));
  const discount_total = toMoney(pricedLineItems.reduce((total, item) => {
    const discountAmount = item.quantity * item.list_price * (item.discount_percent / 100);
    return total + discountAmount;
  }, 0));
  const discountedSubtotal = subtotal - discount_total;
  const tax_total = toMoney(discountedSubtotal * (normalizedTaxPercent / 100));
  const grand_total = toMoney(discountedSubtotal + tax_total);

  return {
    line_items: pricedLineItems,
    subtotal,
    discount_total,
    tax_total,
    grand_total,
  };
}

function createQuote({
  tenant_id,
  opportunity_id,
  currency,
  valid_until,
  line_items,
  status = 'draft',
  tax_percent = 0,
}) {
  const timestamp = nowIso();
  const quote_id = `qte_${randomUUID()}`;

  const pricing = computeQuotePricing(line_items, tax_percent);

  const quote = {
    quote_id,
    tenant_id,
    opportunity_id,
    status,
    currency,
    subtotal: pricing.subtotal,
    discount_total: pricing.discount_total,
    tax_total: pricing.tax_total,
    grand_total: pricing.grand_total,
    valid_until,
    created_at: timestamp,
    accepted_at: null,
    line_items: pricing.line_items,
  };

  quotes.set(quote_id, quote);
  return quote;
}

function listQuotes(tenantId) {
  return Array.from(quotes.values()).filter((quote) => quote.tenant_id === tenantId);
}

function getQuoteById(tenantId, quoteId) {
  const quote = quotes.get(quoteId);
  if (!quote || quote.tenant_id !== tenantId) return null;
  return quote;
}

function acceptQuote(tenantId, quoteId) {
  const quote = getQuoteById(tenantId, quoteId);
  if (!quote) return null;

  quote.status = 'accepted';
  quote.accepted_at = nowIso();
  return quote;
}

function createOrderFromQuote(quote) {
  const timestamp = nowIso();
  const order_id = `ord_${randomUUID()}`;

  const order = {
    order_id,
    tenant_id: quote.tenant_id,
    quote_id: quote.quote_id,
    opportunity_id: quote.opportunity_id,
    status: 'created',
    currency: quote.currency,
    subtotal: quote.subtotal,
    discount_total: quote.discount_total,
    tax_total: quote.tax_total,
    grand_total: quote.grand_total,
    ordered_at: quote.accepted_at,
    created_at: timestamp,
    line_items: quote.line_items,
  };

  orders.set(order_id, order);
  return order;
}

function listOrders(tenantId) {
  return Array.from(orders.values()).filter((order) => order.tenant_id === tenantId);
}

function getOrderById(tenantId, orderId) {
  const order = orders.get(orderId);
  if (!order || order.tenant_id !== tenantId) return null;
  return order;
}

module.exports = {
  createQuote,
  listQuotes,
  getQuoteById,
  acceptQuote,
  createOrderFromQuote,
  listOrders,
  getOrderById,
  computeQuotePricing,
};
