import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";

/**
 * Renders a scrollable list of items and scrolls to the item with `scrollToId`.
 * Each item is `{ id, component }`: `id` is used for keying and scroll tracking,
 * `component` is the rendered content.
 */
function AutoScrollList({ items, scrollToId }) {
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
        {items.map(({ id, component }) => (
          <List.Item key={String(id)} data-scroll-id={String(id)}>
            {component}
          </List.Item>
        ))}
      </List>
    </div>
  );
}

AutoScrollList.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      component: PropTypes.node.isRequired,
    }),
  ).isRequired,
  scrollToId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default AutoScrollList;