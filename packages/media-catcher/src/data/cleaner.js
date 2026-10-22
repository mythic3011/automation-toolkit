/**
 * JSON data cleaning functionality
 */

import { USELESS_VALUES } from "../core/config.js";
import { state } from "../core/state.js";

/**
 * Clean JSON data by removing useless fields
 */
export function cleanJSON(data) {
  if (!state.cleanData) return data;

  const cleanObject = (obj) => {
    // Handle arrays
    if (Array.isArray(obj)) {
      const cleaned = [];
      for (let i = 0, len = obj.length; i < len; i++) {
        const item = cleanObject(obj[i]);
        if (item !== undefined) cleaned.push(item);
      }
      return cleaned;
    }

    // Handle objects
    if (obj !== null && typeof obj === "object") {
      const cleaned = {};
      for (const key in obj) {
        if (!Object.prototype.hasOwnProperty.call(obj, key)) continue;

        const value = obj[key];

        // Skip useless values
        if (USELESS_VALUES.has(value)) continue;

        // Recursively clean nested objects
        if (typeof value === "object" && value !== null) {
          const cleanedValue = cleanObject(value);
          const hasContent = Array.isArray(cleanedValue)
            ? cleanedValue.length > 0
            : Object.keys(cleanedValue).length > 0;

          if (hasContent) cleaned[key] = cleanedValue;
        } else {
          cleaned[key] = value;
        }
      }
      return cleaned;
    }

    return obj;
  };

  return cleanObject(data);
}
