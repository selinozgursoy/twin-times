import {DEFAULT_PROFILE} from '../data/profile.js';
import {DEFAULT_SOURCES} from '../data/sources.js';
const DEFAULTS={profile:DEFAULT_PROFILE,sources:DEFAULT_SOURCES,stories:[],newsmarks:[],engagements:[],lastRefresh:null};
export async function getState(){const x=await chrome.storage.local.get(Object.keys(DEFAULTS));return Object.fromEntries(Object.entries(DEFAULTS).map(([k,v])=>[k,x[k]??structuredClone(v)]));}
export async function ensureDefaults(){const x=await chrome.storage.local.get(Object.keys(DEFAULTS));const patch={};for(const [k,v] of Object.entries(DEFAULTS))if(x[k]===undefined)patch[k]=structuredClone(v);if(Object.keys(patch).length)await chrome.storage.local.set(patch);}
export async function patchState(p){await chrome.storage.local.set(p);}
export async function engage(storyId,action,extra={}){const {engagements=[]}=await chrome.storage.local.get('engagements');engagements.push({storyId,action,at:new Date().toISOString(),...extra});await chrome.storage.local.set({engagements:engagements.slice(-2500)});}
export async function toggleNewsmark(story){const {newsmarks=[]}=await chrome.storage.local.get('newsmarks');const i=newsmarks.findIndex(x=>x.id===story.id||x.url===story.url);let marked;if(i>=0){newsmarks.splice(i,1);marked=false;}else{newsmarks.unshift({...story,newsmarkedAt:new Date().toISOString()});marked=true;}await chrome.storage.local.set({newsmarks:newsmarks.slice(0,500)});await engage(story.id,marked?'newsmark':'unnewsmark');return {marked,count:newsmarks.length};}
