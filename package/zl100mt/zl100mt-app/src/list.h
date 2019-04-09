
#ifndef _WLH_LIST_H
#define _WLH_LIST_H

#if 0
#define iot_offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#define iot_container_of(ptr, type, member) ({			\
	const typeof( ((type *)0)->member ) *__mptr = (ptr);	\
	(type *)( (char *)__mptr - iot_offsetof(type,member) );})
#endif

#define iot_container_of(ptr, type, member) \
    ((type*)(((char *)ptr) - ((char *)&(((type *)0)->member))))
// #define iot_container_of(ptr, type, member) (type *)((size_t)(ptr) - iot_offsetof(type,member))

/*
 * These are non-NULL pointers that will result in page faults
 * under normal circumstances, used to verify that nobody uses
 * non-initialized list entries.
 */
#define IOT_LIST_POISON1  ((void *) 0x00100100)
#define IOT_LIST_POISON2  ((void *) 0x00200200)


/*
 * A list is a bi-directional link chain of 'struct list_head'.
 * A head is a place holder which doesn't belong to another
 * struct holding meaningful data.
 *
 *  head    entry1    entry2        last entry
 *
 *   ___      ___      ___            ___
 *   |_|<====>|_|<====>|_|     ...    |_|<====>/\
 *            |_|      |_|            |_|     /||\
 *   /\       |_|      |_|            |_|      ||
 *  /||\      |_|      |_|            |_|      ||
 *   ||                                        ||
 *  \||/                                      \||/
 *   \/ <====================================> \/
 *
 * An empty list is the one whose 'next' and 'prev' both point to itself.
 */

typedef struct struc_iot_list_head {
	struct struc_iot_list_head *next, *prev;
} T_IOT_LISTHEAD;

struct _struc_iot_hlist_node {
	struct _struc_iot_hlist_node *next, **pprev;
};

struct struc_iot_hlist_head {
	struct _struc_iot_hlist_node *first;
};

/*
 * [Internal only]
 *         this macro is used to evaluate a list head.
 *         don't use this macro independently.
 *         for internal use only.
 */
#define IOT_LIST_HEAD_INIT(name) { &(name), &(name) }

/*
 * [Interface]
 *         claim a list head 'name' and initialize it as empty.
 */
#define IOT_LIST_HEAD(name) \
	T_IOT_LISTHEAD name = IOT_LIST_HEAD_INIT(name)


/*
 * [Interface]
 *         initialize 'list' as empty. 'list' is claimed elsewhere.
 */
static inline void IOT_INIT_LIST_HEAD(T_IOT_LISTHEAD *list)
{
	list->next = list;
	list->prev = list;
}

/*
 * [Internal only]
 *         add 'n' entry before 'next' and after 'prev'.
 *         'prev' and 'next' must be adjacent nodes on a chain.
 *         'prev' and 'next' can be a head or a real entry.
 */
static inline void __iot_list_add(T_IOT_LISTHEAD *n,
			      T_IOT_LISTHEAD *prev,
			      T_IOT_LISTHEAD *next)
{
	next->prev = n;
	n->next = next;
	n->prev = prev;
	prev->next = n;
}

/*
 * [Internal only]
 *         Delink the entry between 'prev' and 'next' from the chain.
 *         Called only where we know the prev/next entries already!
 */
static inline void __iot_list_del(T_IOT_LISTHEAD * prev, T_IOT_LISTHEAD * next)
{
	next->prev = prev;
	prev->next = next;
}

/*
 * [Interface]
 *     Append 'n' node after 'ref' node on a list.
 *     'n' : new stand alone node to be inserted
 *     'ref' : node on a list, after which 'new' is inserted
 */
static inline void iot_list_add(T_IOT_LISTHEAD *n, T_IOT_LISTHEAD *ref)
{
	__iot_list_add(n, ref, ref->next);
}

/*
 * [Interface]
 *     Insert 'n' node before 'ref' node on a list.
 *     'n' : new stand alone node to be added
 *     'ref' : node on the list, before which 'new' is inserted.
 */
static inline void iot_list_add_tail(T_IOT_LISTHEAD *n, T_IOT_LISTHEAD *ref)
{
	__iot_list_add(n, ref->prev, ref);
}

/*
 * [Interface]
 *     delink 'entry' from list and set pointers as uninitialized.
 *     'entry' : a node on a list, to be deleted.
 *
 *     After the calling, list_empty() on this entry doesn't return
 *     true. The entry is in a uninitialized state.
 *
 * Note: Caller ensures entry is in a list or empty.
 */
static inline void iot_list_del(T_IOT_LISTHEAD *entry)
{
	__iot_list_del(entry->prev, entry->next);
	IOT_INIT_LIST_HEAD(entry);
}

/*
 * [Internal only]
 *     replace 'old' node by 'n' node in a list.
 *     'old' : the node on a list to be replaced
 *     'n' : the new stnad alone node to insert
 *
 * Note: ensure 'old' is in a list and 'n' is stand alone.
 */
static inline void __iot_list_replace(T_IOT_LISTHEAD *old,
				T_IOT_LISTHEAD *n)
{
	n->next = old->next;
	n->next->prev = n;
	n->prev = old->prev;
	n->prev->next = n;
}

/*
 * [Interface]
 *     replace 'old' node on a list with a stand alone 'n' node.
 *     After calling, 'old' entry is in uninitialized state.
 *     'old' : a node in a list which is to be replaced.
 *     'n' : a stand alone node which is to be inserted.
 * Note: Caller ensures 'old' is in a list and 'n' is stand alone.
 */
static inline void iot_list_replace(T_IOT_LISTHEAD *old,
					T_IOT_LISTHEAD *n)
{
	__iot_list_replace(old, n);
	IOT_INIT_LIST_HEAD(old);
}

/*
 * [Interface]
 *     delete 'entry' from it's own list and append it after 'ref'
 *     'entry' : the node to move.
 *     'ref'   : the node after which 'entry' is inserted.
 *
 * Note: ensure 'entry' and 'ref' are both in a list, either the same list or different ones.
 */
static inline void iot_list_move(T_IOT_LISTHEAD *entry, T_IOT_LISTHEAD *ref)
{
	iot_list_del(entry);
	iot_list_add(entry, ref);
}

/*
 * [Interface]
 *     Same as list_move() except that 'entry' is inserted before 'ref'
 *     'entry' : the entry to move
 *     'ref'   : the entry before which 'entry' is inserted
 *
 * Note: ensure 'entry' and 'ref' are both in a list, either the same list or different ones.
 */
static inline void iot_list_move_before(T_IOT_LISTHEAD *entry,
				  T_IOT_LISTHEAD *ref)
{
	iot_list_del(entry);
	iot_list_add_tail(entry, ref);
}

/*
 * [Interface]
 *     tests whether 'entry' is the last entry in list 'head'
 *     'entry' : the entry to test
 *     'head'  : must be the head of a list
 */
static inline int iot_list_is_last(const T_IOT_LISTHEAD *entry,
				const T_IOT_LISTHEAD *head)
{
	return (entry->next == head);
}

/*
 * [Interface]
 *     tests whether 'entry' is the last entry in list 'head'
 *     'entry' : the entry to test
 *     'head'  : must be the head of a list
 */
static inline int iot_list_is_first(const T_IOT_LISTHEAD *entry,
				const T_IOT_LISTHEAD *head)
{
	return (head->next == entry);
}

#define iot_list_next_link(head) (head->next)

static inline T_IOT_LISTHEAD *iot_list_1st_link_or_null(const T_IOT_LISTHEAD *head)
{
	T_IOT_LISTHEAD *p_link = iot_list_next_link(head);
	return (iot_list_is_first(p_link, head) ? NULL : p_link);
}

/*
 * luheng[Interface]
 *     tests whether list 'head' is empty (only place holder existent)
 *     'head' : must be the head of a list.
 *
 * Note: This function checks 'head''s next pointer only.
 */
static inline int iot_list_empty(const T_IOT_LISTHEAD *head)
{
	return head->next == head;
}

/*
 * luheng[Interface]
 *     tests whether a list is empty and not being modified
 *     'head' : must be the head of a list.
 *
 * Note: This function checks both 'head''s next and prev pointers.
 */
static inline int iot_list_empty_careful(const T_IOT_LISTHEAD *head)
{
	T_IOT_LISTHEAD *next = head->next;
	return (next == head) && (next == head->prev);
}

/*
 * luheng[Interface]
 *     rotate the list to the left. move the 1st entry to the tail.
 *     'head' : the head(place holder) of the list
 */
static inline void iot_list_rotate_left(T_IOT_LISTHEAD *head)
{
	T_IOT_LISTHEAD *first;

	if (!iot_list_empty(head)) {
		first = head->next;
		iot_list_move_before(first, head);
	}
}

/*
 * luheng[Interface]
 *     tests whether a list has just one entry.
 *     'head' : the list to test.
 */
static inline int iot_list_is_singular(const T_IOT_LISTHEAD *head)
{
	return !iot_list_empty(head) && (head->next == head->prev);
}

static inline void __iot_list_cut_position(T_IOT_LISTHEAD *list,
		T_IOT_LISTHEAD *head, T_IOT_LISTHEAD *entry)
{
	T_IOT_LISTHEAD *new_first = entry->next;
	list->next = head->next;
	list->next->prev = list;
	list->prev = entry;
	entry->next = list;
	head->next = new_first;
	new_first->prev = head;
}

/**
 * luheng[Interface]
 *     list_cut_position - cut a list into two
 *     'list'  : a new list to add all removed entries
 *     'head'  : head(place holder) of a list with entries
 *     'entry' : an entry in the list, could be the head itself
 *	             and if so we won't cut the list
 *
 * This func cuts the initial part of 'head' list, from the 1st entry to and
 * including 'entry'. After calling,  'list' points to the rest part and 'head'
 * points to the cut-off part.
 *
 * Note: 'list' must be an empty list or a list you do not care about
 *     losing its data.  'entry' must be in the list 'head'.
 *
 */
static inline void iot_list_cut_position(T_IOT_LISTHEAD *list,
		T_IOT_LISTHEAD *head, T_IOT_LISTHEAD *entry)
{
	if (iot_list_empty(head))
		return;

	if (iot_list_is_singular(head) &&
		(head->next != entry && head != entry))
		return;

	if (entry == head)
		IOT_INIT_LIST_HEAD(list);
	else
		__iot_list_cut_position(list, head, entry);
}

/*
 * [Internal only]
 *     insert the all entries(excluding head itself) of 'list'
 *     between 'prev' and 'next'.
 *
 * Note: 'prev' and 'next' must be in another list and adjacent. After
 *       calling, list is empty.
 */
static inline void __iot_list_splice(const T_IOT_LISTHEAD *list,
				 T_IOT_LISTHEAD *prev,
				 T_IOT_LISTHEAD *next)
{
	T_IOT_LISTHEAD *first = list->next;
	T_IOT_LISTHEAD *last = list->prev;

	first->prev = prev;
	prev->next = first;

	last->next = next;
	next->prev = last;
}

/*
 * [Internal only]
 *     join 'list' in front of 'head' node.
 *     'list' : the new list to add.
 *     'head' : the place after which 'list' is inserted.
 *
 * Precondition:
 *     'list' must be the head(place holder) of a complete list.
 *     'head' can be a head(place holder) or a real entry.
 *
 * Aftermath:
 *     All real entries of 'list' are inserted after 'head'.
 */
static inline void iot_list_splice(const T_IOT_LISTHEAD *list,
				T_IOT_LISTHEAD *head)
{
	if (!iot_list_empty(list))
		__iot_list_splice(list, head, head->next);
}

/*
 * [Internal only]
 *     The same as iot_list_splice() except that:
 *         contents of 'list' are inserted before 'head' node but not after
 *         'head' node.
 *
 * Aftermath:
 *     All real entries of 'list' are inserted before 'head'.
 */
static inline void iot_list_splice_tail(T_IOT_LISTHEAD *list,
				T_IOT_LISTHEAD *head)
{
	if (!iot_list_empty(list))
		__iot_list_splice(list, head->prev, head);
}

/*
 * [Interface]
 *     safe wrapper of internal iot_list_splice() by initializing 'list'
 *     after splice.
 */
static inline void iot_list_splice_init(T_IOT_LISTHEAD *list,
				    T_IOT_LISTHEAD *head)
{
	if (!iot_list_empty(list)) {
		__iot_list_splice(list, head, head->next);
		IOT_INIT_LIST_HEAD(list);
	}
}

/*
 * [Interface]
 *     safe wrapper of internal iot_list_splice_tail() by initializing 'list'
 *     after splice.
 */
static inline void iot_list_splice_tail_init(T_IOT_LISTHEAD *list,
					 T_IOT_LISTHEAD *head)
{
	if (!iot_list_empty(list)) {
		__iot_list_splice(list, head->prev, head);
		IOT_INIT_LIST_HEAD(list);
	}
}

/* [Interface]
 *     get the struct for this entry
 *     'ptr'    : the 'T_IOT_LISTHEAD' pointer.
 *     'type'   : the type of the struct this is embedded in.
 *     'member' : the field name of the list_struct within the struct.
 */
#define iot_list_entry(ptr, type, member) \
	iot_container_of(ptr, type, member)

/*
 * [Interface]
 *     get the first element from 'head', the head(place holder) of a list
 *     'head':   the list head(place holder) to take the element from.
 *     'type':   the type of the parent data struct that list_head is embedded in.
 *     'member': the name of the list_struct within the parent data struct.
 *
 * Note, ensure that the list is not empty.
 */
#define iot_list_first_entry(head, type, member) \
	iot_list_entry((head)->next, type, member)

/*
 * [Interface]
 *     The same as iot_list_first_entry() except that 'head' can be empty.
 *     If the list is empty, it returns NULL.
 */
#define iot_list_first_entry_or_null(head, type, member) \
	(!iot_list_empty(head) ? iot_list_first_entry(head, type, member) : NULL)

/*
 * [Interface]
 *     iterate nodes over a list, the node cannot be removed during loop
 *     iteration doesn't include 'head'(place holder) itself.
 *     'pos':  loop cursor node.
 *     'head': the head of a list.
 */
#define iot_list_for_each(pos, head) \
	for (pos = (head)->next; pos != (head); pos = pos->next)

/*
 * [Interface]
 *     The same as iot_list_first_entry() except the direction is backwards.
 */
#define iot_list_for_each_prev(pos, head) \
	for (pos = (head)->prev; pos != (head); pos = pos->prev)

/*
 * [Interface]
 *     The same as iot_list_first_entry() except that the node can be removed during loop.
 */
#define iot_list_for_each_safe(pos, n, head) \
	for (pos = (head)->next, n = pos->next; pos != (head); \
		pos = n, n = pos->next)

/*
 * [Interface]
 *     The same as iot_list_for_each_prev() except that the node can be removed during loop.
 */
#define iot_list_for_each_prev_safe(pos, n, head) \
	for (pos = (head)->prev, n = pos->prev; \
	     pos != (head); \
	     pos = n, n = pos->prev)

/*
 * [Interface]
 * iterate elements over a list of given type
 * 'pos'    : the ptr to parent data struct as a loop cursor.
 * 'head'   : the head(place holder) for your list.
 * 'member' : the name of the list_struct within the parent struct.
 */
#define iot_list_for_each_entry(pos, head, member, type)				\
	for (pos = iot_list_entry((head)->next, typeof(*pos), member);	\
	     &pos->member != (head); 	\
	     pos = iot_list_entry(pos->member.next, typeof(*pos), member))

/*
 * The same as list_for_each_entry() except that the direction is backwards.
 */
#define iot_list_for_each_entry_reverse(pos, head, member)			\
	for (pos = iot_list_entry((head)->prev, typeof(*pos), member);	\
	     &pos->member != (head); 	\
	     pos = iot_list_entry(pos->member.prev, typeof(*pos), member))


#if 0
/****************************** wangluheng ******************************/
/**
 * list_prepare_entry - prepare a pos entry for use in list_for_each_entry_continue()
 * @pos:	the type * to use as a start point
 * @head:	the head of the list
 * @member:	the name of the list_struct within the struct.
 *
 * Prepares a pos entry for use as a start point in list_for_each_entry_continue().
 */
#define list_prepare_entry(pos, head, member) \
	((pos) ? : iot_list_entry(head, typeof(*pos), member))

/**
 * list_for_each_entry_continue - continue iteration over list of given type
 * @pos:	the type * to use as a loop cursor.
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Continue to iterate over list of given type, continuing after
 * the current position.
 */
#define list_for_each_entry_continue(pos, head, member) 		\
	for (pos = iot_list_entry(pos->member.next, typeof(*pos), member);	\
	     &pos->member != (head);	\
	     pos = iot_list_entry(pos->member.next, typeof(*pos), member))

/**
 * list_for_each_entry_continue_reverse - iterate backwards from the given point
 * @pos:	the type * to use as a loop cursor.
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Start to iterate over list of given type backwards, continuing after
 * the current position.
 */
#define list_for_each_entry_continue_reverse(pos, head, member)		\
	for (pos = iot_list_entry(pos->member.prev, typeof(*pos), member);	\
	     &pos->member != (head);	\
	     pos = iot_list_entry(pos->member.prev, typeof(*pos), member))

/**
 * list_for_each_entry_from - iterate over list of given type from the current point
 * @pos:	the type * to use as a loop cursor.
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Iterate over list of given type, continuing from current position.
 */
#define list_for_each_entry_from(pos, head, member) 			\
	for (; &pos->member != (head);	\
	     pos = iot_list_entry(pos->member.next, typeof(*pos), member))

/**
 * list_for_each_entry_safe - iterate over list of given type safe against removal of list entry
 * @pos:	the type * to use as a loop cursor.
 * @n:		another type * to use as temporary storage
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 */
#define list_for_each_entry_safe(pos, n, head, member)			\
	for (pos = iot_list_entry((head)->next, typeof(*pos), member),	\
		n = iot_list_entry(pos->member.next, typeof(*pos), member);	\
	     &pos->member != (head); 					\
	     pos = n, n = iot_list_entry(n->member.next, typeof(*n), member))

/**
 * list_for_each_entry_safe_continue - continue list iteration safe against removal
 * @pos:	the type * to use as a loop cursor.
 * @n:		another type * to use as temporary storage
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Iterate over list of given type, continuing after current point,
 * safe against removal of list entry.
 */
#define list_for_each_entry_safe_continue(pos, n, head, member) 		\
	for (pos = iot_list_entry(pos->member.next, typeof(*pos), member), 		\
		n = iot_list_entry(pos->member.next, typeof(*pos), member);		\
	     &pos->member != (head);						\
	     pos = n, n = iot_list_entry(n->member.next, typeof(*n), member))

/**
 * list_for_each_entry_safe_from - iterate over list from current point safe against removal
 * @pos:	the type * to use as a loop cursor.
 * @n:		another type * to use as temporary storage
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Iterate over list of given type from current point, safe against
 * removal of list entry.
 */
#define list_for_each_entry_safe_from(pos, n, head, member) 			\
	for (n = iot_list_entry(pos->member.next, typeof(*pos), member);		\
	     &pos->member != (head);						\
	     pos = n, n = iot_list_entry(n->member.next, typeof(*n), member))

/**
 * list_for_each_entry_safe_reverse - iterate backwards over list safe against removal
 * @pos:	the type * to use as a loop cursor.
 * @n:		another type * to use as temporary storage
 * @head:	the head for your list.
 * @member:	the name of the list_struct within the struct.
 *
 * Iterate backwards over list of given type, safe against removal
 * of list entry.
 */
#define list_for_each_entry_safe_reverse(pos, n, head, member)		\
	for (pos = iot_list_entry((head)->prev, typeof(*pos), member),	\
		n = iot_list_entry(pos->member.prev, typeof(*pos), member);	\
	     &pos->member != (head); 					\
	     pos = n, n = iot_list_entry(n->member.prev, typeof(*n), member))

/**
 * list_safe_reset_next - reset a stale list_for_each_entry_safe loop
 * @pos:	the loop cursor used in the list_for_each_entry_safe loop
 * @n:		temporary storage used in list_for_each_entry_safe
 * @member:	the name of the list_struct within the struct.
 *
 * list_safe_reset_next is not safe to use in general if the list may be
 * modified concurrently (eg. the lock is dropped in the loop body). An
 * exception to this is if the cursor element (pos) is pinned in the list,
 * and list_safe_reset_next is called after re-taking the lock and before
 * completing the current iteration of the loop body.
 */
#define list_safe_reset_next(pos, n, member)				\
	n = iot_list_entry(pos->member.next, typeof(*pos), member)

/*
 * Double linked lists with a single pointer list head.
 * Mostly useful for hash tables where the two pointer list head is
 * too wasteful.
 * You lose the ability to access the tail in O(1).
 */

#define HLIST_HEAD_INIT { .first = NULL }
#define HLIST_HEAD(name) struct struc_iot_hlist_head name = {  .first = NULL }
#define INIT_HLIST_HEAD(ptr) ((ptr)->first = NULL)
static inline void INIT_HLIST_NODE(struct _struc_iot_hlist_node *h)
{
	h->next = NULL;
	h->pprev = NULL;
}

static inline int hlist_unhashed(const struct _struc_iot_hlist_node *h)
{
	return !h->pprev;
}

static inline int hlist_empty(const struct struc_iot_hlist_head *h)
{
	return !h->first;
}

static inline void __hlist_del(struct _struc_iot_hlist_node *n)
{
	struct _struc_iot_hlist_node *next = n->next;
	struct _struc_iot_hlist_node **pprev = n->pprev;
	*pprev = next;
	if (next)
		next->pprev = pprev;
}

static inline void hlist_del(struct _struc_iot_hlist_node *n)
{
	__hlist_del(n);
	n->next = IOT_LIST_POISON1;
	n->pprev = IOT_LIST_POISON2;
}

static inline void hlist_del_init(struct _struc_iot_hlist_node *n)
{
	if (!hlist_unhashed(n)) {
		__hlist_del(n);
		INIT_HLIST_NODE(n);
	}
}

static inline void hlist_add_head(struct _struc_iot_hlist_node *n, struct struc_iot_hlist_head *h)
{
	struct _struc_iot_hlist_node *first = h->first;
	n->next = first;
	if (first)
		first->pprev = &n->next;
	h->first = n;
	n->pprev = &h->first;
}

/* next must be != NULL */
static inline void hlist_add_before(struct _struc_iot_hlist_node *n,
					struct _struc_iot_hlist_node *next)
{
	n->pprev = next->pprev;
	n->next = next;
	next->pprev = &n->next;
	*(n->pprev) = n;
}

static inline void hlist_add_after(struct _struc_iot_hlist_node *n,
					struct _struc_iot_hlist_node *next)
{
	next->next = n->next;
	n->next = next;
	next->pprev = &n->next;

	if(next->next)
		next->next->pprev  = &next->next;
}

/* after that we'll appear to be on some hlist and hlist_del will work */
static inline void hlist_add_fake(struct _struc_iot_hlist_node *n)
{
	n->pprev = &n->next;
}

/*
 * Move a list from one list head to another. Fixup the pprev
 * reference of the first entry if it exists.
 */
static inline void hlist_move_list(struct struc_iot_hlist_head *old,
				   struct struc_iot_hlist_head *new)
{
	new->first = old->first;
	if (new->first)
		new->first->pprev = &new->first;
	old->first = NULL;
}

#define hlist_entry(ptr, type, member) iot_container_of(ptr,type,member)

#define hlist_for_each(pos, head) \
	for (pos = (head)->first; pos ; pos = pos->next)

#define hlist_for_each_safe(pos, n, head) \
	for (pos = (head)->first; pos && ({ n = pos->next; 1; }); \
	     pos = n)

#define hlist_entry_safe(ptr, type, member) \
	({ typeof(ptr) ____ptr = (ptr); \
	   ____ptr ? hlist_entry(____ptr, type, member) : NULL; \
	})

/**
 * hlist_for_each_entry	- iterate over list of given type
 * @pos:	the type * to use as a loop cursor.
 * @head:	the head for your list.
 * @member:	the name of the _struc_iot_hlist_node within the struct.
 */
#define hlist_for_each_entry(pos, head, member)				\
	for (pos = hlist_entry_safe((head)->first, typeof(*(pos)), member);\
	     pos;							\
	     pos = hlist_entry_safe((pos)->member.next, typeof(*(pos)), member))

/**
 * hlist_for_each_entry_continue - iterate over a hlist continuing after current point
 * @pos:	the type * to use as a loop cursor.
 * @member:	the name of the _struc_iot_hlist_node within the struct.
 */
#define hlist_for_each_entry_continue(pos, member)			\
	for (pos = hlist_entry_safe((pos)->member.next, typeof(*(pos)), member);\
	     pos;							\
	     pos = hlist_entry_safe((pos)->member.next, typeof(*(pos)), member))

/**
 * hlist_for_each_entry_from - iterate over a hlist continuing from current point
 * @pos:	the type * to use as a loop cursor.
 * @member:	the name of the _struc_iot_hlist_node within the struct.
 */
#define hlist_for_each_entry_from(pos, member)				\
	for (; pos;							\
	     pos = hlist_entry_safe((pos)->member.next, typeof(*(pos)), member))

/**
 * hlist_for_each_entry_safe - iterate over list of given type safe against removal of list entry
 * @pos:	the type * to use as a loop cursor.
 * @n:		another &struct _struc_iot_hlist_node to use as temporary storage
 * @head:	the head for your list.
 * @member:	the name of the _struc_iot_hlist_node within the struct.
 */
#define hlist_for_each_entry_safe(pos, n, head, member) 		\
	for (pos = hlist_entry_safe((head)->first, typeof(*pos), member);\
	     pos && ({ n = pos->member.next; 1; });			\
	     pos = hlist_entry_safe(n, typeof(*pos), member))
#endif


#endif
