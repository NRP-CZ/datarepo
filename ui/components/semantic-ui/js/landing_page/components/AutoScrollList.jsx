import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
import "../../../less/components/auto-scroll-list.less";

/**
 * Renders a scrollable list of items and scrolls to the item with `scrollToId` Id.
 * Therefore, `items` objects are expected to have `id`.
 */
function AutoScrollList({ items, scrollToId, renderItem }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!scrollToId || !containerRef.current) {
      return;
    }

    const item = containerRef.current.querySelector(
      `[data-scroll-id="${CSS.escape(String(scrollToId))}"]`,
    );

    if (item) {
      item.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [scrollToId]);

  return (
    <div ref={containerRef} className="auto-scroll-list">
      <List bulleted relaxed>
        {items.map((item) => (
          <List.Item
            key={String(item.id)}
            data-scroll-id={String(item.id)}
          >
            {renderItem(item)}
          </List.Item>
        ))}
      </List>
    </div>
  );
}

AutoScrollList.propTypes = {
  items: PropTypes.array.isRequired,
  scrollToId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  renderItem: PropTypes.func.isRequired,
};

export default AutoScrollList;